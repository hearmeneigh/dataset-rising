from typing import List, Optional
import os


def split_posts(samples: List[str], limit: Optional[int], shards: int) -> List[str]:
    count = 0
    base_dir = os.path.dirname(samples[0])

    shard_filenames = [os.path.join(base_dir, f'.tmp.shard_{i}.jsonl') for i in range(shards)]
    shard_fp = [open(fn, 'wt') for fn in shard_filenames]

    for sample_file in samples:
        if limit is not None and count >= limit:
            continue

        with open(sample_file, 'rt') as ap:
            for line in ap:
                shard_fp[count % shards].write(line)

                if limit is not None and count >= limit:
                    continue

                count += 1

    for fp in shard_fp:
        fp.close()

    return shard_filenames
