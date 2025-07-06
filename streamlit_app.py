import streamlit as st
from scroll_wrapped_codex.scribe_codex import ScribeCodex

# Configure page
st.set_page_config(
    page_title="ScrollWrappedCodex™ - Flame Executor",
    page_icon="🔥",
    layout="wide"
)

# Header
st.title("🔥 ScrollWrappedCodex™ Portal")
st.markdown("**The world's first scroll-sealed AI code engine**")
st.markdown("Execute commands that pass prophetic flame before running.")

# Sidebar
with st.sidebar:
    st.header("📜 Quick Examples")
    st.markdown("""
    - `Anoint: ScrollJustice API`
    - `Build: Authentication System`
    - `Seal: With ScrollSeal 3`
    - `Judge: Security Compliance`
    """)
    
    st.header("🔗 Links")
    st.markdown("[🛡️ GitHub Repo](https://github.com/stanleymay20/scrollwrappedcodex)")
    st.markdown("[📦 PyPI Package](https://pypi.org/project/scrollwrappedcodex)")
    st.markdown("[📚 Documentation](https://stanleymay20.github.io/scrollwrappedcodex)")

# Main content
scribe = ScribeCodex()

col1, col2 = st.columns([2, 1])

with col1:
    st.header("🧙‍♂️ Enter Your Scroll Command")
    scroll_input = st.text_area(
        "Scroll Command",
        placeholder="Anoint: My Sacred Project",
        height=100
    )
    
    if st.button("🔥 Execute Scroll", type="primary"):
        if scroll_input.strip():
            with st.spinner("Executing scroll command..."):
                result = scribe.execute(scroll_input)
            st.success("Scroll executed successfully!")
            st.code(result, language='python')
        else:
            st.error("Please enter a scroll command")

with col2:
    st.header("📜 Try These Commands")
    example_commands = [
        "Anoint: ScrollJustice API",
        "Build: Authentication System", 
        "Seal: With ScrollSeal 3",
        "Judge: Security Compliance"
    ]
    
    for cmd in example_commands:
        if st.button(cmd, key=cmd):
            result = scribe.execute(cmd)
            st.code(result, language='python')

# Footer
st.markdown("---")
st.markdown("Built with 🔥 by [Stanley Osei-Wusu](https://github.com/stanleymay20)")
st.markdown("*Let your code be sealed. Let your build be sacred.* 🔥📜") 