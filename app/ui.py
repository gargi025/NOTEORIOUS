import streamlit as st
from PIL import Image

from app.graph_visualizer import draw_knowledge_graph
from app.pipeline import HandwritingPipeline


st.set_page_config(
    page_title="NOTEORIOUS",
    layout="wide"
)


st.title("NOTEORIOUS")

st.markdown(
    """
    ### Turning handwritten notes into verified knowledge

    Upload a handwritten note and NOTEORIOUS will:

    1. Detect handwritten text lines
    2. Recognize the handwriting
    3. Estimate OCR confidence
    4. Check semantic consistency
    5. Check knowledge-graph consistency
    6. Calculate an overall reliability score
    7. Decide whether the result should be accepted or reviewed
    """
)


uploaded_file = st.file_uploader(
    "Upload a handwritten note",
    type=["png", "jpg", "jpeg"]
)


if uploaded_file:

    image = Image.open(
        uploaded_file
    ).convert("RGB")

    st.subheader("Uploaded Note")

    st.image(
        image,
        use_container_width=True
    )

    if st.button(
        "Process Note",
        type="primary"
    ):

        image_path = "data/samples/current_upload.png"

        image.save(image_path)

        with st.spinner(
            "Analyzing handwritten note..."
        ):

            pipeline = HandwritingPipeline()

            output = pipeline.process(
                image_path
            )

            results = output["lines"]
            graph = output["graph"]

        st.success(
            f"Detected {len(results)} text lines."
        )

        # ==================================================
        # RECOGNIZED KNOWLEDGE
        # ==================================================

        st.subheader("Recognized Knowledge")

        for result in results:

            st.divider()

            col1, col2 = st.columns(
                [2, 1]
            )

            # ----------------------------------------------
            # Recognized text
            # ----------------------------------------------

            with col1:

                st.markdown(
                    f"### Line {result['line_number']}"
                )

                st.write(
                    result["text"]
                )

            # ----------------------------------------------
            # Reliability signals
            # ----------------------------------------------

            with col2:

                st.metric(
                    "OCR Confidence",
                    f"{result['confidence']:.1%}"
                )

                st.metric(
                    "Semantic Consistency",
                    f"{result['semantic_score']:.1%}"
                )

                kg_status = (
                    "✓ Consistent"
                    if result["kg_consistent"]
                    else "✕ Conflict"
                )

                st.metric(
                    "KG Consistency",
                    kg_status
                )

                st.metric(
                    "Overall Reliability",
                    f"{result['reliability_score']:.1%}"
                )

            # ----------------------------------------------
            # KG conflicts
            # ----------------------------------------------

            if result["kg_conflicts"]:

                st.error(
                    "⚠ Knowledge Graph Conflict Detected"
                )

                for conflict in result["kg_conflicts"]:

                    st.write(
                        f"Existing: "
                        f"`{conflict['source']}` "
                        f"--[{conflict['relation']}]--> "
                        f"`{conflict['existing_target']}`"
                    )

                    st.write(
                        f"Candidate: "
                        f"`{conflict['source']}` "
                        f"--[{conflict['relation']}]--> "
                        f"`{conflict['candidate_target']}`"
                    )

            # ----------------------------------------------
            # Final decision
            # ----------------------------------------------

            if result["action"] == "ACCEPT":

                st.success(
                    "✓ ACCEPT — High reliability"
                )

            elif result["action"] == "VERIFY":

                st.warning(
                    "⚠ VERIFY — Potentially unreliable knowledge"
                )

            else:

                st.error(
                    "✕ ASK — Student verification required"
                )

        # ==================================================
        # KNOWLEDGE GRAPH
        # ==================================================

        st.divider()

        st.subheader("Knowledge Graph")

        if len(graph.nodes) == 0:

            st.info(
                "No relationships could be extracted "
                "from the recognized text yet."
            )

        else:

            st.write(
                f"Extracted {len(graph.nodes)} concepts "
                f"and {len(graph.edges)} relationships."
            )

            figure = draw_knowledge_graph(
                graph
            )

            st.pyplot(
                figure,
                use_container_width=True
            )