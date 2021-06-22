<h3>Build</h3>
<code>docker build -t domain_checker .</code>
<hr>
<h3>Run</h3>
<code>docker run -it -v $(pwd):/data/output domain_checker</code>
<hr>
<p>The name of input file must be <code>domains.csv</code>.
The name of result file is <code>result.csv</code>.
</p>
