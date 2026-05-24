# FastApi-NextJs-Workout

```bash
fastApi run main.py --host localhost

### Run testcases verify 90% pass

```bash
cd /dev
pip install -r requirements.txt
cd fastapi && pytest --junitxml=pytest-report.xml -v
cd .. && python .github/scripts/check_test_pass_rate.py fastapi/pytest-report.xml 0.90