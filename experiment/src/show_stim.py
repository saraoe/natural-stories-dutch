"""
functions for showing stimuli in psychopy scripts
"""
from psychopy import core, event


def show_fixation(stim, win, sec):
    stim.draw()
    win.flip()
    core.wait(sec)


def show_blackscreen(win, sec):
    win.flip()
    core.wait(sec)


def show_text(word: str, text_stim, win):
    text_stim.text = word
    text_stim.draw()
    win.flip()
    key = event.waitKeys()[0]
    if key in ["escape", "q"]:
        win.close()
        core.quit()


def show_word(word: str, text_stim, win, stopwatch):
    text_stim.text = word
    text_stim.draw()
    win.flip()
    stopwatch.reset()
    key = event.waitKeys()[0]
    rt = stopwatch.getTime()
    if key in ["escape", "q"]:
        win.close()
        core.quit()
    return rt
