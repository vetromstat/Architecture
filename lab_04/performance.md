# Performance test

|                 |               |            |
|-----------------|---------------|------------|
| Metric          | Without Redis | With Redis |
| Duration        | 30s           | 30s        |
| Threads         | 4             | 4          |
| Connections     | 100           | 100        |
| Avg Latency     | 112.67ms      | 29.85ms    |
| Latency Stdev   | 92.48ms       | 9.64ms     |
| Max Latency     | 1.08s         | 340.25ms   |
| Latency Stdev   | 93.38%        | 96.07%     |
| Avg Req/Sec     | 254.98        | 890        |
| Req/Sec Stdev   | 161.30        | 126.77     |
| Max Req/Sec     | 870           | 1.23k      |
| Req/Sec Stdev   | 65.46%        | 70.48%     |
| Total Requests  | 26,456        | 99,148     |
| Total Data Read | 6.35MB        | 27.22MB    |
| Requests/sec    | 1001.34       | 3640.87    |
| Transfer/sec    | 235.62KB      | 936KB      |
