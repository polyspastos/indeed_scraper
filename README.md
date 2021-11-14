### What is this?
\
A webcrawler for job ads on indeed. As [jobfunnel](https://github.com/PaulMcInnis/JobFunnel) is broken at the moment because of captchas, a workaround was needed.
<br>
<br>

### How does it work?  
<br>

```python
pip install requirements.txt
py scraper.py --locale=gb --city=London --radius=100 --must-contain=remote
```

\
parameter help with adding
```
--help
```

### todos:
- proper restructuring
- revise selenium functionality
- more parameters