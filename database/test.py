from time import sleep

# from progress.spinner import Spinner
# from alive_progress import alive_bar

# bar = alive_bar(None, title='Hello world', length=40, bar='smooth', spinner='dots_waves', force_tty=True).__enter__()
#
# while True:
#     bar()
#     sleep(0.1)


#
from halo import Halo

bar = Halo(text='Loading', spinner='dots4')
bar.start()

for i in range(100):
    sleep(0.1)

bar.succeed('Done')

#

# from tqdm import tqdm
# t = tqdm(unit=' tags', desc='Importing tags', dynamic_ncols=True)
#
# for i in range(10):
#     t.update()
#     sleep(0.1)
#
# t.colour = 'green'
# t.update()
# t.close()
#
