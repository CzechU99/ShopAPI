# Load Testing Artifacts

Use this folder to keep every screenshot and export that demonstrates the Lab 4 experiments. Follow the naming scheme from the assignment so reviewers can quickly map evidence to each step:

```
docs/load-tests/
  01-prep-delay.png
  02-timeout-180s.png
  03-maxconn-10-pool-0s.png
  03-maxconn-100-pool-100ms.png
  04-keepalive-10.png
  04-keepalive-50.png
  05-http1.png
  05-http2.png
  06-slow-postgres.png
```

Feel free to add more PNGs (for example, Loki log views or Tempo traces) as long as the prefix makes it obvious which experiment they belong to.

> Screenshots are not committed yet — capture them after running k6 and drop them into this directory before turning in the lab.
