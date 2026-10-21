# 维护方法

需要 Python 3.10 或更新版本，以及系统时区数据库。GitHub Actions 使用 Python 3.12，无需安装第三方包，也不用配置账号密钥。

修改正文请编辑 `README.template.md`，然后运行：

```bash
python3 -m unittest discover -s tests -v
python3 scripts/update.py
```

`README.md` 和 `data/latest.json` 由脚本生成。脚本只向固定的 52id.org 地区接口发请求，白名单输出数量、状态分类、地区入口和北京时间；不落盘完整接口响应。统计是接口快照，不是独立登录检测结果。

创建空的公开仓库（默认分支 main）后，把这些文件推送上去。在 Actions 页找到“每日同步网站状态”，点击 Run workflow 验证一次。若账号或组织策略禁止 Actions 写入，请在仓库 Settings → Actions → General 核对工作流权限及分支保护规则。

默认每天北京时间 00:00 运行。改时间请调整 `.github/workflows/daily-update.yml` 的 UTC cron。README 时间和 commit 日期均使用 Asia/Shanghai。

请求失败会让任务失败，旧快照保留，去 Actions 查看失败记录。不要为了让任务显示成功而填充虚构账号数量。GitHub 对公开仓库的长期无活动定时任务有停用机制；如果任务停用，在 Actions 重新启用并核对 GitHub 当前规则。

上线前检查首页文案和文章链接。正文不自动调用生成式模型，不填“稳定运行天数”，不承诺实时检测或永久可用。
