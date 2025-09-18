import streamlit as st
import base64
import os
import time
import fitz
from utils.redaction_utils import redact_prenuvo_pdf
from supabase_utils import get_user_supabase, build_supabase_path
import io
from datetime import datetime
import streamlit.components.v1 as components

def prenuvo_tab(username, timepoint_id="T_01", timepoint_modifier="T01"):
    st.markdown(f"<h1>{timepoint_modifier} Prenuvo</h1>", unsafe_allow_html=True)
    
    # Check if this is T02 - no data collected
    if timepoint_id == "T_02":
        st.info("No Prenuvo data were collected for Time Point 02.")
        return
    
    user_supabase = get_user_supabase()
    filename = build_supabase_path(username, timepoint_id, "redacted_prenuvo_report.pdf")
    bucket = user_supabase.storage.from_("data")
    file_list = bucket.list(path=f"{username}/{timepoint_modifier}/")
    file_exists = any(f["name"] == "redacted_prenuvo_report.pdf" for f in file_list)
    
    if file_exists:
        st.success("Your report was successfully redacted and saved!")
        try:
            pdf_bytes = bucket.download(filename)
            if isinstance(pdf_bytes, bytes):
                st.download_button("Download Report", pdf_bytes, file_name="redacted_prenuvo_report.pdf")
            else:
                st.error("Failed to retrieve the file. Please try again.")
        except Exception as e:
            st.error(f"Error retrieving file: {e}")
    elif "redacted_pdf_for_review" in st.session_state:
        file_bytes = st.session_state.redacted_pdf_for_review
        st.markdown("""
            <div style='font-size:17.5px; line-height:1.6; margin-top:0.5rem; margin-bottom:1.5rem;'>
            <strong>Please Review Your Redacted Report:</strong> Browse through each page to ensure sensitive information has been removed. Click "Approve Redaction" to save the file to your account.
            </div>
        """, unsafe_allow_html=True)
        base64_pdf = base64.b64encode(file_bytes).decode("utf-8")
        st.markdown(f"""
            <div style='font-size:17.5px; line-height:1.6; margin-bottom:1rem;'>
            <a href="data:application/pdf;base64,{base64_pdf}" download="redacted_prenuvo_report.pdf">Click here to download your redacted report.</a><br>
            Or scroll through the preview below to review each page.
            </div>
        """, unsafe_allow_html=True)
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        page_images = [
            page.get_pixmap(dpi=150).tobytes("png")
            for page in doc
            if page.get_text().strip()
        ]
        doc.close()
        img_html_blocks = [
            f"<img src='data:image/png;base64,{base64.b64encode(img).decode()}' style='width:100%; margin-bottom: 1.5rem;'/>"
            for img in page_images
        ]
        scrollable_html = f"""
        <div style='height:650px; overflow-y:scroll; border:1px solid #ccc; padding:12px; background-color:#f9f9f9;'>
            {''.join(img_html_blocks)}
        </div>
        """
        components.html(scrollable_html, height=670, scrolling=False)
        if st.button("Approve Redaction", key="approve_redaction"):
            with st.spinner("Saving redacted file..."):
                try:
                    bucket.upload(filename, file_bytes, {"content-type": "application/pdf"})
                    st.session_state.pop("redacted_pdf_for_review", None)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to save redacted file: {e}")
        if st.button("Report an Issue", key="report_issue"):
            st.session_state.show_report_box = True
        if st.button("Start Over", key="start_over_before_approve"):
            st.session_state.pop("redacted_pdf_for_review", None)
            st.rerun()
        if st.session_state.get("show_report_box") and not st.session_state.get("issue_submitted"):
            issue = st.text_area("Describe the issue with redaction:")
            if st.button("Submit Issue", key="submit_issue"):
                timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S-%f")
                bucket.upload(
                    f"{username}/issues/issue_{timestamp}.txt",
                    issue.encode("utf-8"),
                    {"content-type": "text/plain"}
                )
                st.session_state.issue_submitted = True
                st.session_state.pop("show_report_box", None)
                st.rerun()
        if st.session_state.get("issue_submitted"):
            st.success("Issue submitted.")
    else:
        st.markdown("<div style='font-size:17.5px; line-height:1.6'>Please upload your Prenuvo Physician Report:</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='font-size:15px; line-height:1.6; margin-bottom:0.5rem; padding-left:1.5rem'>
          <ol style="margin-top: 0; margin-bottom: 0;">
            <li>Log in to <a href='https://login.prenuvo.com/' target='_blank'>Prenuvo</a></li>
            <li>Click <strong>View Official Physician Report</strong></li>
            <li>Download the PDF</li>
            <li>Upload it below</li>
          </ol>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='font-size:17.5px; line-height:1.6'>We will redact sensitive information and prepare a version for your review.</div>", unsafe_allow_html=True)
        uploaded = st.file_uploader("", type="pdf", key="prenuvo_upload")
        if uploaded:
            with st.spinner("Redacting sensitive information..."):
                input_path = "/tmp/prenuvo_original.pdf"
                output_path = "/tmp/prenuvo_redacted.pdf"
                with open(input_path, "wb") as f:
                    f.write(uploaded.read())
                redact_prenuvo_pdf(input_path, output_path)
                os.remove(input_path)
                with open(output_path, "rb") as f:
                    pdf_bytes = f.read()
                os.remove(output_path)
                st.session_state.redacted_pdf_for_review = pdf_bytes
                for k in ["approved_redaction", "issue_submitted", "show_report_box"]:
                    st.session_state.pop(k, None)
                time.sleep(1.5)
                st.rerun() 
