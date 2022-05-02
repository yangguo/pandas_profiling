from turtle import update
import streamlit as st
import pandas as pd
import pandas_profiling
from streamlit_pandas_profiling import st_profile_report

upload_file = st.file_uploader("文件上传", type=["csv", "txt"])

if upload_file is not None:
    st.write("已上传文件信息：", upload_file)
    # read file
    df = pd.read_csv(upload_file)
    # show data
    st.write(df)
    pr = df.profile_report()

    st_profile_report(pr)
