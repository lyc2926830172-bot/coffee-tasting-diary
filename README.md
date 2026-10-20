# 一杯之间 咖啡品鉴日记

这是一个基于 Flask 和 SQLite 的个人咖啡品鉴记录网站，用于保存咖啡豆档案、冲煮参数、风味感受和品鉴复盘。

## 功能

- 咖啡豆档案：名称、产地、品种、烘焙度、处理法、烘焙商和备注。
- 品鉴日记：冲煮方式、粉水参数、水温、香气、风味、心情和复盘。
- 五维评分：酸质、甜感、醇厚度、余韵和整体喜爱度。
- 风味洞察：展示个人感官评分均值、常见产地和常用冲煮方式。
- CSV 导出：可下载全部品鉴记录。

## 作业要求核对

| 要求 | 项目实现 |
| --- | --- |
| Python Web 框架 | Flask |
| 至少 3 种访问路由 | `/`、`/beans`、`/notes`、`/insights`、`/export/diary.csv` 等 |
| 至少 2 个数据表 | `coffee_beans` 与 `tasting_notes`，一对多关系 |
| 至少 2 个 HTML 模板 | 共 5 个：基础模板、首页、豆子档案、品鉴日记、风味洞察 |

## 本地运行

需要 Python 3.10 或更高版本。在项目根目录执行：

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

保持终端窗口开启，并在浏览器访问 `http://127.0.0.1:5000/`。首次启动会自动生成 `coffee_diary.db` 和两条示例品鉴数据。

## 测试

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
