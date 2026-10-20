from __future__ import annotations

import csv
import io
import os
from datetime import date, datetime

from flask import Flask, Response, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.environ.get("COFFEE_DIARY_DATABASE", os.path.join(BASE_DIR, "coffee_diary.db"))
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("COFFEE_DIARY_SECRET", "replace-this-secret-before-production")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DATABASE_PATH
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class CoffeeBean(db.Model):
    __tablename__ = "coffee_beans"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    origin = db.Column(db.String(80), nullable=False)
    variety = db.Column(db.String(60), nullable=False, default="未记录")
    roast_level = db.Column(db.String(30), nullable=False)
    process_method = db.Column(db.String(50), nullable=False, default="水洗")
    roaster = db.Column(db.String(80), nullable=False, default="未记录")
    purchase_date = db.Column(db.Date, nullable=True)
    bean_note = db.Column(db.String(300), nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.relationship("TastingNote", back_populates="bean", cascade="all, delete-orphan")

class TastingNote(db.Model):
    __tablename__ = "tasting_notes"
    id = db.Column(db.Integer, primary_key=True)
    bean_id = db.Column(db.Integer, db.ForeignKey("coffee_beans.id"), nullable=False)
    tasting_date = db.Column(db.Date, nullable=False, default=date.today)
    brewing_method = db.Column(db.String(40), nullable=False)
    dose = db.Column(db.String(30), nullable=False, default="")
    water_temperature = db.Column(db.String(30), nullable=False, default="")
    aroma = db.Column(db.String(150), nullable=False, default="")
    flavor_notes = db.Column(db.String(200), nullable=False)
    acidity = db.Column(db.Integer, nullable=False)
    sweetness = db.Column(db.Integer, nullable=False)
    body = db.Column(db.Integer, nullable=False)
    aftertaste = db.Column(db.Integer, nullable=False)
    overall_score = db.Column(db.Integer, nullable=False)
    mood = db.Column(db.String(30), nullable=False, default="平静")
    reflection = db.Column(db.String(400), nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    bean = db.relationship("CoffeeBean", back_populates="notes")

BREWING_METHODS = ("手冲", "意式浓缩", "法压壶", "爱乐压", "冷萃", "虹吸壶")
ROAST_LEVELS = ("浅烘焙", "中浅烘焙", "中烘焙", "中深烘焙", "深烘焙")
MOODS = ("平静", "专注", "愉悦", "清醒", "慵懒")

def parse_date(value: str) -> date | None:
    return datetime.strptime(value, "%Y-%m-%d").date() if value else None

def valid_score(value: int | None) -> bool:
    return value is not None and 1 <= value <= 5

@app.route("/")
def dashboard():
    latest_notes = TastingNote.query.order_by(TastingNote.tasting_date.desc(), TastingNote.id.desc()).limit(4).all()
    average_score = db.session.query(func.avg(TastingNote.overall_score)).scalar() or 0
    favorite = db.session.query(CoffeeBean.origin, func.count(TastingNote.id)).join(TastingNote).group_by(CoffeeBean.origin).order_by(func.count(TastingNote.id).desc()).first()
    return render_template("dashboard.html", latest_notes=latest_notes, bean_count=CoffeeBean.query.count(), note_count=TastingNote.query.count(), average_score=average_score, favorite_origin=favorite[0] if favorite else "等待第一杯记录")

@app.route("/beans", methods=["GET", "POST"])
def beans():
    if request.method == "POST":
        name, origin, roast = request.form.get("name", "").strip(), request.form.get("origin", "").strip(), request.form.get("roast_level", "")
        if not name or not origin or roast not in ROAST_LEVELS:
            flash("请填写咖啡豆名称、产地并选择烘焙度。", "error")
        else:
            try:
                db.session.add(CoffeeBean(name=name, origin=origin, variety=request.form.get("variety", "").strip() or "未记录", roast_level=roast, process_method=request.form.get("process_method", "").strip() or "水洗", roaster=request.form.get("roaster", "").strip() or "未记录", purchase_date=parse_date(request.form.get("purchase_date", "")), bean_note=request.form.get("bean_note", "").strip()))
                db.session.commit(); flash("新的咖啡豆档案已保存。", "success")
                return redirect(url_for("beans"))
            except ValueError: flash("购买日期格式不正确。", "error")
    return render_template("beans.html", beans=CoffeeBean.query.order_by(CoffeeBean.created_at.desc()).all(), roast_levels=ROAST_LEVELS)

@app.route("/notes", methods=["GET", "POST"])
def notes():
    bean_list = CoffeeBean.query.order_by(CoffeeBean.name).all()
    if request.method == "POST":
        bean_id = request.form.get("bean_id", type=int)
        scores = {key: request.form.get(key, type=int) for key in ("acidity", "sweetness", "body", "aftertaste", "overall_score")}
        if not bean_id or not db.session.get(CoffeeBean, bean_id): flash("请选择已建立档案的咖啡豆。", "error")
        elif request.form.get("brewing_method") not in BREWING_METHODS: flash("请选择正确的冲煮方式。", "error")
        elif not request.form.get("flavor_notes", "").strip() or not all(valid_score(v) for v in scores.values()): flash("请填写风味描述，并为每个维度选择 1 到 5 分。", "error")
        else:
            try:
                db.session.add(TastingNote(bean_id=bean_id, tasting_date=parse_date(request.form.get("tasting_date", "")) or date.today(), brewing_method=request.form["brewing_method"], dose=request.form.get("dose", "").strip(), water_temperature=request.form.get("water_temperature", "").strip(), aroma=request.form.get("aroma", "").strip(), flavor_notes=request.form["flavor_notes"].strip(), mood=request.form.get("mood", "平静"), reflection=request.form.get("reflection", "").strip(), **scores))
                db.session.commit(); flash("这一杯的风味记忆已经收进日记。", "success")
                return redirect(url_for("notes"))
            except ValueError: flash("品鉴日期格式不正确。", "error")
    selected_method, selected_bean = request.args.get("method", ""), request.args.get("bean", type=int)
    query = TastingNote.query.order_by(TastingNote.tasting_date.desc(), TastingNote.id.desc())
    if selected_method in BREWING_METHODS: query = query.filter_by(brewing_method=selected_method)
    if selected_bean and db.session.get(CoffeeBean, selected_bean): query = query.filter_by(bean_id=selected_bean)
    return render_template("notes.html", notes=query.all(), beans=bean_list, methods=BREWING_METHODS, moods=MOODS, selected_method=selected_method, selected_bean=selected_bean, today=date.today().isoformat())

@app.post("/notes/<int:note_id>/delete")
def delete_note(note_id: int):
    db.session.delete(db.get_or_404(TastingNote, note_id)); db.session.commit()
    flash("这条品鉴记录已删除。", "success")
    return redirect(url_for("notes"))

@app.route("/insights")
def insights():
    averages = {"酸质": db.session.query(func.avg(TastingNote.acidity)).scalar() or 0, "甜感": db.session.query(func.avg(TastingNote.sweetness)).scalar() or 0, "醇厚度": db.session.query(func.avg(TastingNote.body)).scalar() or 0, "余韵": db.session.query(func.avg(TastingNote.aftertaste)).scalar() or 0, "整体喜爱": db.session.query(func.avg(TastingNote.overall_score)).scalar() or 0}
    origins = db.session.query(CoffeeBean.origin, func.count(TastingNote.id).label("total")).join(TastingNote).group_by(CoffeeBean.origin).order_by(func.count(TastingNote.id).desc()).all()
    methods = db.session.query(TastingNote.brewing_method, func.count(TastingNote.id).label("total")).group_by(TastingNote.brewing_method).order_by(func.count(TastingNote.id).desc()).all()
    return render_template("insights.html", averages=averages, origins=origins, methods=methods)

@app.route("/export/diary.csv")
def export_diary():
    output = io.StringIO(); writer = csv.writer(output)
    writer.writerow(["日期", "咖啡豆", "产地", "烘焙度", "冲煮方式", "风味", "酸质", "甜感", "醇厚度", "余韵", "总分", "心情", "复盘"])
    for note in TastingNote.query.order_by(TastingNote.tasting_date.desc()).all(): writer.writerow([note.tasting_date, note.bean.name, note.bean.origin, note.bean.roast_level, note.brewing_method, note.flavor_notes, note.acidity, note.sweetness, note.body, note.aftertaste, note.overall_score, note.mood, note.reflection])
    return Response("\ufeff" + output.getvalue(), mimetype="text/csv; charset=utf-8", headers={"Content-Disposition": "attachment; filename=coffee-diary.csv"})

def seed_data():
    if CoffeeBean.query.count(): return
    first = CoffeeBean(name="耶加雪菲 花冠", origin="埃塞俄比亚", variety="原生种", roast_level="浅烘焙", process_method="日晒", roaster="山谷烘焙", bean_note="适合慢慢降温后感受花香和莓果调。")
    second = CoffeeBean(name="慧兰 小农拼配", origin="哥伦比亚", variety="卡杜拉", roast_level="中浅烘焙", process_method="水洗", roaster="晨光咖啡", bean_note="干净、平衡，适合日常手冲。")
    db.session.add_all([first, second]); db.session.flush()
    db.session.add_all([TastingNote(bean_id=first.id, tasting_date=date.today(), brewing_method="手冲", dose="15g / 240ml", water_temperature="91°C", aroma="橙花、熟桃", flavor_notes="草莓果酱、柑橘、红茶", acidity=5, sweetness=4, body=3, aftertaste=4, overall_score=5, mood="愉悦", reflection="前段注水柔和一些，尾段的红茶感更清晰。"), TastingNote(bean_id=second.id, tasting_date=date.today(), brewing_method="爱乐压", dose="16g / 220ml", water_temperature="88°C", aroma="焦糖、坚果", flavor_notes="太妃糖、可可、黄糖", acidity=3, sweetness=4, body=4, aftertaste=4, overall_score=4, mood="平静", reflection="浸泡 90 秒后压出，口感圆润，适合午后。")]); db.session.commit()

with app.app_context(): db.create_all(); seed_data()
if __name__ == "__main__": app.run(debug=True)
