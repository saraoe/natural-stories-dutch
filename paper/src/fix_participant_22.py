'''
Fixing Sampling rate and excess channels for participant 22
'''

import os
import mne

# load data
data_raw_file = (os.path.join("data", "spr", "TCMR_EEG_22.bdf"))
raw22 = mne.io.read_raw_bdf(data_raw_file)
print(raw22.info)

# Select the slice of relevant channels from the channel list, drop the rest
Ch_names_list = raw22.ch_names
Redundant_ch = Ch_names_list[70:]
Redundant_ch.pop() #Make sure the event channel 'Status' is not removed
raw22.drop_channels(ch_names=Redundant_ch)

# Create a copy of the raw data resampled at 512 Hz, and rename channels to be consistant with other data (takes a while to run)
Resampled = raw22.copy().resample(sfreq = 512)
Resampled.rename_channels({"F1-0":"F1", 'F3-0':'F3', 'F5-0':'F5', 'F7-0':'F7','F2-0':'F2', 'F4-0':'F4', 'F6-0':'F6', 'F8-0':'F8'})
print(Resampled.info)

# Check if all events are still present
events = mne.find_events(raw22)
events_rs = mne.find_events(Resampled)
if not (events[:, 2] == events_rs[:, 2]).all():
    print("Warning: Event codes doesn't match between original and down sampled version of the file!")

# save resampled data
mne.export.export_raw(os.path.join("data", "spr", "TCMR_EEG_22.edf") , Resampled)

