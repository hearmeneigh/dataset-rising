## Troubleshooting

### Multi GPU Hangs
On some systems, NCCL can cause hangs. Try disabling NCCL with:

```bash
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1

python train.py ...
```
