# parse a qlog file
#
# we want to draw graphs containing multiple paths
#
# we would like the logs to show:
# - CWIN
# - Bytes in flight
# - latest RTT sample
# - cumulative data
#
# we are getting these data from parsing the qlog file.

import sys
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class cc_state:
    def __init__(self):
        self.event_time = 0
        self.cwnd = 0
        self.bytes_in_flight = 0
        self.pacing_rate = 0
        self.smoothed_rtt = 0
        self.min_rtt = 0
        self.latest_rtt = 0
        self.app_limited = 0

    def cc_update(self, event_time, cc_data):
        self.event_time = event_time
        for x in cc_data:
            if x == 'cwnd':
                self.cwnd = int(cc_data[x])
            elif x == 'bytes_in_flight':
                self.bytes_in_flight = int(cc_data[x])
            elif x == 'pacing_rate':
                self.pacing_rate = int(cc_data[x])
            elif x == 'smoothed_rtt':
                self.smoothed_rtt = int(cc_data[x])
            elif x == 'min_rtt':
                self.min_rtt = int(cc_data[x])
            elif x == 'latest_rtt':
                self.latest_rtt = int(cc_data[x])
            elif x == 'app_limited':
                self.app_limited = int(cc_data[x])
            else:
                print("Unexpected cc element: " + x)

    def cc_vector(self):
        v = [
            self.event_time,
            self.cwnd,
            self.bytes_in_flight,
            self.pacing_rate,
            self.smoothed_rtt,
            self.min_rtt,
            self.latest_rtt,
            self.app_limited ]
        return v

    def cc_headers():
        headers = [
            'event_time',
            'cwnd',
            'bytes_in_flight',
            'pacing_rate',
            'smoothed_rtt',
            'min_rtt',
            'latest_rtt',
            'app_limited'
        ]
        return headers


class qlog_event:
    def __init__(self):
        self.event_time = 0
        self.category = ""
        self.event = ""
        self.data = ""
        self.path_id = -1

    def load_event(self, ev, ef, reference_time):
        is_good = True
        if len(ef) != len(ev):
            print("error. Only " + str(len(ev)) + " elements in event: " + str(ev))
            is_good = False
        else:
            for i in range(0, len(ef)):
                evt = ef[i]
                if evt == 'relative_time':
                    self.event_time = ev[i] + reference_time
                elif evt == 'path_id':
                    self.path_id = ev[i]
                elif evt == 'category':
                    self.category = ev[i]
                elif evt == 'event':
                    self.event = ev[i]
                elif evt == 'data':
                    self.data = ev[i]
                else:
                    print("Unexpected event element: " + evt + ": " + str(ev[i]))
                    is_good = False
        return is_good
    def print_event(self):
        print("[ " + str(self.event_time) + ", " + str(self.path_id) + ", " + self.category + ", " + self.event + ", data ]")

class path:
    def __init__(self):
        self.events = []
        self.cc_state = cc_state()
        self.cc_log = []
        self.path_id = -1

class qlog_trace:
    def __init__(self):
        self.ef = []
        self.reference_time = 0
        self.paths = {}

    def load_event_fields(self, ef):
        self.ef = ef
        print(str(ef))

    def load_common(self, cf):
        if "reference_time" in cf:
            self.reference_time = int(cf["reference_time"])
            print("reference_time:" + str(self.reference_time))
        else:
            print(str(cf))

    def load(self, trc):
        for x in trc:
            print(x)
            if x == "event_fields":
                self.load_event_fields(trc[x])
            elif x == "common_fields":
                self.load_common(trc[x])
            elif x == "events":
                print(str(len(trc[x])) + " events")
                evts = trc[x]
                for i in range(0, len(trc[x])):
                    evx = qlog_event()
                    if not evx.load_event(evts[i], self.ef, self.reference_time):
                        print("Error load event " + str(i))
                        break
                    else:
                        if evx.path_id not in self.paths:
                            self.paths[evx.path_id] = path()
                        self.paths[evx.path_id].events.append(evx)
                        if evx.category == "recovery" and evx.event == "metrics_updated":
                            self.paths[evx.path_id].cc_state.cc_update(evx.event_time, evx.data)
                            self.paths[evx.path_id].cc_log.append(self.paths[evx.path_id].cc_state.cc_vector())

                for path_id in self.paths:
                    print("Loaded " + str(len(self.paths[path_id].events)) + " events.")
                    print("Loaded " + str(len(self.paths[path_id].cc_log)) + " cc_logs.")
            else:
                print(str(trc[x]))


def qlog_parse(file_name):
    with open(file_name,"r") as F:
        qlog_object = json.load(F)
        for x in qlog_object:
            print(x)
            if x == "qlog_version":
                print(str(qlog_object[x]))
            elif x == "title":
                print(str(qlog_object[x]))
            elif x == "traces":
                trcs = qlog_object[x]
                for i in range(0, len(trcs)):
                    trace = qlog_trace()
                    trace.load(trcs[i])
                    return trace

    return None

def trace_one_graph(trace):
    tdf = pd.DataFrame(trace.cc_log, columns=cc_state.cc_headers())
    # Prepare a subtrace with cwnd and bytes in flight
    axa = tdf.plot.scatter(x="event_time", y="cwnd", alpha=0.5, logx=False, logy=False, color="blue")
    tdf.plot.scatter(ax=axa, x="event_time", y="bytes_in_flight", xlabel="time(us)", ylabel="bytes", alpha=0.5, color="orange")
    plt.legend(["cwnd", "bytes_in_flight"])  
    plt.show()

def trace_graphs(tdfs, df_names, f_name=""):
    colors1 = ["blue", "green", "violet", "red", "orange"]
    colors2 = ["turquoise", "lime", "magenta", "pink", "yellow" ]
    dashes = ['solid', 'dashed', 'dashdot', 'dotted', 'dotted' ]
    markers = [ 'o', '+', 'x', '^', '.' ]
    i_max = len(tdfs)
    if i_max > 5:
        i_max = 5
    legends = []
    # Prepare a subtrace with cwnd and bytes in flight
    fig, axes = plt.subplots(2, gridspec_kw={'height_ratios': [3, 1]}, figsize=(8, 5), sharex=True, layout='constrained')
    axes.flatten()
    #fig.tight_layout()
    for i in range(0, i_max):
        l1 = "cwin, " + df_names[i]    
        l2 = "bytes in flight, " + df_names[i]
        l3 = "rtt, " + df_names[i]
        l4 = "min rtt, " + df_names[i]

        tdfs[i].plot.scatter(ax=axes[0], x="event_time", y="bytes_in_flight", s=15, marker=markers[i], xlabel="time(us)", ylabel="bytes", alpha=0.5, color=colors2[i], label=l2)
        tdfs[i].plot.line(ax=axes[0], x="event_time", y="cwnd", linewidth=2, linestyle=dashes[i], alpha=0.75, xlabel="time(us)", ylabel="bytes", color=colors1[i], label=l1)       
        tdfs[i].plot.line(ax=axes[1], x="event_time", y="latest_rtt", linewidth=2, linestyle=dashes[i], alpha=0.75, xlabel="time(us)", ylabel="us", color=colors1[i], label=l3)     
        tdfs[i].plot.line(ax=axes[1], x="event_time", y="min_rtt", linewidth=1, linestyle=dashes[i], alpha=0.75, xlabel="time(us)", ylabel="us", color=colors2[i], label=l4)
    #plt.legend(legends)
    if len(f_name) == 0:
        plt.show()
    else:
        plt.savefig(f_name)

tdfs = []
tdf_names = []

# assume that the first argument is the input qlog, and the second argument the name of the output file

if len(sys.argv) > 1:
    trc = qlog_parse(sys.argv[1])
    f_name = sys.argv[2] if len(sys.argv) > 2 else ""

    for path_id in trc.paths:
        tdf = pd.DataFrame(trc.paths[path_id].cc_log, columns=cc_state.cc_headers())
        tdfs.append(tdf)
        tdf_names.append('path_' + str(path_id))

    trace_graphs(tdfs, tdf_names, f_name=f_name)
