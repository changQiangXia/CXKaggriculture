# cap2 quote-reorder floor audit

A narrow ablation disabled `_r37_reorder_sales` after step 360 only when MILK, WOOL and STRAWBERRY prices were all below 20, leaving all route actions and other guards unchanged. This targeted the common premium-price collapse seen in losses while avoiding earlier market timing.

Fixed-opponent replay results on the five latest cap2 losses (using `info.seed` and `steps[t+1]`):

| episode | cap2 margin | floor margin | delta |
|---:|---:|---:|---:|
|108607985|-1898|-1898|0|
|108606917|-10208|-10208|0|
|108602848|-2077|-2146|-69|
|108600815|-1196|-1196|0|
|108599773|-5954|-5954|0|

The rule did not improve any loss and worsened one. It is rejected and will not enter the candidate queue.
