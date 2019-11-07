import os
from uuid import uuid4

import pandas as pd
import dash_html_components as html
import dash_core_components as dcc
import webviz_core_components as wcc
from dash.dependencies import Input, Output
from webviz_config.webviz_store import webvizstore
from webviz_config.common_cache import CACHE
from webviz_config import WebvizContainerABC

import fmu.ensemble

class Completions(WebvizContainerABC):
    """### Completion viewer

This container will provide a viewer for the well completions as they
have been configured in an Eclipse deck.

This needs ensembles configured in container_settings
"""

    def __init__(self, app, container_settings):

        self.uid = f"{uuid4()}"
        self.chart_id = "chart-id-{}".format(uuid4())
        #self.plot_type_id = "plot-type-id-{}".format(uuid4())
        #self.disk_usage = get_disk_usage(self.scratch_dir)
        self.ensemble_paths = container_settings["scratch_ensembles"]
        self.dropdown_ens_id = f"dropdown-ens-{self.uid}"
        self.dropdown_real_id = f"dropdown-real-{self.uid}"
        self.set_callbacks(app)
        print("INitialized completions")

    @property
    def layout(self):
        return html.Div(
            [
                html.P(f"Completion view on {self.ensemble_paths}"),
                wcc.Graph(id=self.chart_id),
            ]
        )

    def set_callbacks(self, app):
        #@app.callback(
        #    Output(self.chart_id, "figure"), [Input(self.plot_type_id, "value")]
        #)
        def _update_plot(plot_type):
            print("updating plot")
            print(get_realization_compdat(self.ensemble_paths, "foo", 0))
            if plot_type == "Pie chart":
                data = [
                    {
                        "values": self.usage,
                        "labels": self.users,
                        "text": (self.usage).map("{:.2f} GB".format),
                        "textinfo": "label",
                        "textposition": "inside",
                        "hoverinfo": "label+text",
                        "type": "pie",
                    }
                ]
                layout = {}
            layout["height"] = 800
            layout["width"] = 1000
            layout["font"] = {"family": "Equinor"}
            layout["hoverlabel"] = {"font": {"family": "Equinor"}}

            return {"data": data, "layout": layout}

    def add_webvizstore(self):
        return [(get_disk_usage, [{"scratch_dir": self.scratch_dir}])]

@CACHE.memoize(timeout=CACHE.TIMEOUT)
def scratch_ensemble(ensemble_name, ensemble_path):
    return fmu.ensemble.ScratchEnsemble(ensemble_name, ensemble_path)

def get_compdat(kwargs):
    """Function to be used as callback to an ensemble.

    The function will we called individually on each realization, and
    it can get a handle to the realization object in question through
    kwargs["realization"]

    Upon errors, it should return empty dataframes.
    """
    eclfiles = kwargs["realization"].get_eclfiles()
    if not eclfiles:
        print("Error, could not obtain Eclipse input file for realization x")
        return pd.DataFrame()
    return ecl2df.compdat.df(eclfiles)

@CACHE.memoize(timeout=CACHE.TIMEOUT)
@webvizstore
def get_realization_compdat(ensemble_paths, ensemble_name, realization) -> pd.DataFrame:
    print("extracting compdat")
    assert isinstance(realization, int)
    ens = scratch_ensemble(ens_name, ens_path)
    real = ens[realization]
    return real.apply(get_compdat)
