# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
from streamlit.logger import get_logger
import pandas as pd

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Ana Sayfa",
        page_icon="👋",
    )

    st.write("# İlk Uygulama!-- :balloon: 👋")

    st.sidebar.success("Select a demo above.")
    st.sidebar.balloons()
    st.sidebar.button("Tıkla")
    st.sidebar.markdown("Yan alan yazılar")
    st.sidebar.metric(
        label="ölçüm",
        value=1,
        delta=5,
        delta_color="normal",
        help="Bu ölçüm hakkında bilgi",
        label_visibility="visible",
    )

    st.write(
        pd.DataFrame({"first column": [1, 2, 3, 4], "second column": [10, 20, 30, 40]})
    )
    # st.markdown(
    #     """
    #     Streamlit is an open-source app framework built specifically for
    #     Machine Learning and Data Science projects.
    #     **👈 Select a demo from the sidebar** to see some examples
    #     of what Streamlit can do!
    #     ### Want to learn more?
    #     - Check out [streamlit.io](https://streamlit.io)
    #     - Jump into our [documentation](https://docs.streamlit.io)
    #     - Ask a question in our [community
    #       forums](https://discuss.streamlit.io)
    #     ### See more complex demos
    #     - Use a neural net to [analyze the Udacity Self-driving Car Image
    #       Dataset](https://github.com/streamlit/demo-self-driving)
    #     - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
    # """
    # )


run()
