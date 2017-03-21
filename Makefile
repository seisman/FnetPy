clean:
	find . -name "*.pyc" -exec rm -v {} \;
	rm -rvf __pycache__ *.egg-info
