import streamlit as st
import requests

st.set_page_config(page_title="Travel Itinerary Planner")
st.title("🌍 Travel Itinerary Planner Bot")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "question_index" not in st.session_state:
    st.session_state.question_index = 0

questions = [
    "Where would you like to travel?",
    "What are your travel dates?",
    "How many days do you plan to stay?",
    "What is your estimated budget?",
    "Are you traveling alone, with a partner, or family?",
    "What type of trip do you prefer: relaxation, adventure, culture, or luxury?",
    "Do you have specific destinations in mind?",
    "Do you need visa assistance?",
    "Preferred accommodation type (hotel, hostel, Airbnb, resort)?",
    "Flight class preference (economy, business)?",
    "Do you have any dietary restrictions?",
    "What kind of activities are you interested in?",
    "Any physical limitations we should consider?",
    "Are you open to guided tours?",
    "What's your ideal travel pace: relaxed, moderate, or packed?"
]

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Ask next question
if st.session_state.question_index < len(questions):
    next_question = questions[st.session_state.question_index]
    with st.chat_message("assistant"):
        st.markdown(next_question)
else:
    with st.chat_message("assistant"):
        st.markdown("Thanks for all the info! I'm generating your itinerary...")
    
    # Display contact card at the end
    with st.container():
        st.markdown("---")
        st.markdown("### Contact the Developer")
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image("data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxAQEBAQEBAVEBANDQ0NDQ0NDQ8IEA4NIB0iIiAdHx8kKDQsJCYxJx8fLTMtMSsuMDAwIys0QD81Qyo5Oi4BCgoKDQ0NFQ4PFjcZFRkrKzctNzctNzc3MzctKy03NzcrKy0rKysrLS03Ky0tKys3KystKy0rKysrKystKystK//AABEIAMgAyAMBIgACEQEDEQH/xAAcAAABBQEBAQAAAAAAAAAAAAAAAgMEBQYHAQj/xABAEAABAwIEAwUECAQFBQEAAAABAAIDBBEFEiFBBjFREyJhcYEHkaGxFCMyQlLB0fAkYnKiM2OCkuFDU3OywhX/xAAZAQADAQEBAAAAAAAAAAAAAAAAAQIDBAX/xAAiEQEAAwACAgIDAQEAAAAAAAAAAQIRAyESMRMiBEFRYTL/2gAMAwEAAhEDEQA/AO4oQhACEIQAhCEALwleOcoj3Ep4WnpKlo8fJVtbibwO6APH7SfkCq68aKsRa0q+oxScn/FcP6T2fyUV07zze4+biUmXmkhKUaVnPU+8q0wCV3aEZjbLyuVUqZhE2WQeOiUBsg9KbIoInRBVAm1+SrGnlCxBXqSChxULKQo4qRex335p8FBa9QhCDCEIQAhCEAIQhACEIQAvChBQDciilSZSoxVJkh6q8QOhVm8rmXtS4kbG36JE+0jtZi02ys6eqqET28xri2mgcW5u0cL3EdnAHzWfqOO5NeziaOdi4km6wclSA6+/VNfSuvj42KrIHi3A41qrahlzyNiFOwbjVwlZ24BZms9zLN7vVc1dUbEpMdU4G2x6oyD8X0bFxTAS1gIIfazgQdPFTI2uZKHg3DjqOei+fMHxFzZGHNaz26HlZd2wnF2zMYQQS0hryCHC/ghlyRnbZ08lwPRKldomKR4LR5J15Cz/AG1ifqiMBLlLYSP0UeM95SCVUlU8x4KWoF7G6mRvuomMXEloQhJQQhCAEISXG2p5DmgBzrJHaKvkrbnw2Xn0lZ/JVE2WeZBKhwyg7qTnWkTpxYmRRynnlMlUUo1dIWxyOaMzmsc5rfxOA0C+W66sfJLJJIbySOc55PPMSvqiRfNHG2H9liFWwCwFQ5zQNO6dR81UFDPSu1shkTjoATfoL6qxwzDDJI1pBseZ8Ft4cFjaAA0aWvYbKLcmN6cfk562gk5296TLRvaLkG3WxXTpMMboMugHhyTc+HgixYNPC+iz+Vp8DDcOYYamXsg7K7I5zTa9yNl1WgiNK1jB9pwaXDo5Zbhmi7DEmFvJ0Mx8tFsvtSAnU3W+xNded+RsW8GuwbEDlsf0U2qxAAKvw+n7o8lGxeE5TY/ksqWKdiqww3FQ9xF9Qrd1SLc1iMJZkd4q7qag5dFpMxpU5JztcxyhyfvbUbKkwiUnfdXBOiNa1tsamQyhwuPUdCnFnn13YyA/dJAePBX7XAi43AIU2jGlL6UhCElhVeL1eWzAdTq7yVk9wAJPIAk+SzM82dznHc/BTaJmMhF7ZBTJE4HKPHZSWELGONlByN9lKjmTLQF60BbViYUk514UhiWVouPRmdwaCToGguJ8FwLjn+IqpKtjCI5cuh+0LC1z52Xea6POx7fxsc31IXGauF2UtebZM0ToyANdb/FTe0xjXhpFonfZrDoRHA1zGgOc0EuOuviqqoxCUXealwAcW3jiGRrui12HMjMcY2yNA30svK3BI3AizcriCbsB1WPn326vDY6VGAYvM+7ZHCTnlOTsj6pjGMdlzERljGNuHve0usVa0lA1r+5rlv3rWBKTV4M15ewkBsrg5wN2guSie+1TWfHpB4Xq3ySOe8tcWRSBkjO7cEi+nor2gq/rRc7qMzDI6UXAFyHXIJNyq+kqm9rqVvHddeJ+X9eaHWqCUZRboExiMgsSVVYZiIyjXZQscxUBpuVhW/eKtb6nqepbmOqlVla0N5rmD+IHNlOU6XHIpys4iLtLk8ldotNscc8+Q6lgVYCOfVXrqgW5rmfDuJnKD1WgmxQ5V0eOdN+Pk+qXidWDIADuFqsDmuwNOw08lzanqs0oudwt5hMlgCNre5XevSuC+3mWhQvAULB3K3HZi2MNHORwb/p3VNFSu6q2xFmeUdGNHvP7CeigVeoZzXZU/wBCJ3KdFMR1+auRGgxpDwhVNDuiW2/RT3Rpp8acDxIYU6mwEq6ZQRIsTxfgQeJJY7BxaXPaQbPIHPzW2eVU4iLgjqPgiYiYyTi01nYcgwjECGhhOrbt9QpmJY6Ymi4Jv06LM4uww1EjBoQ91ttLqfhxMtnO1Lb907FYWrG67qXnMeOnfKQ5kmQXJa25cAUmSukheXvkMlxo0OIsE7iVS+FpfEGAjm0PLCfRMCeSSPtZrEZSWgOLtFWRgm3+9tHh87qxh2yx5j57KDg2ByOnIcNAdNtFo/Z5QXpHTvsDUynswbD6oaD43WsoKBofe2voujjiK1x5H5Nfk5fJHo8FAaNNlneKcFeWnLzK6ZHCLKtxOmB2U1ivl6HJx/VyjA+CS83kJ58grDFeB2AXbcHRdGw6kA5BSKumBC18o1hH48eLn3D+CFgynW25V5V4Z3dArmipxfkp0tOLJTbtpXj+uOd0+HubKCeWZbvDLho9FFmohmFuqs6aKwTvbRw0msralfdvlp6L1MUTtbdQhc8u+PRoOu95/mI92iktcqOhrA4k35ud81Y9voiUxaEt0iQZh1VfJUL2Ekp4Xmn9oElxSGhKQNkhySUtyynEPHdFRlzHPMsrdDDCO0sehPIJwTSPKqMWqWRtLpHtY38T3CMfFc0xf2q1MlxBGyEG9nO/iX2+XwWJrK+oqpAZpXSvc4NbncX2J6DZVgzWl4soRPK+RmgdaSN/K7TrfyPNZVzamEkjXTmOi6JxDAIqyeACwjZThn9IjaPyVBUU5OgssZtkzDsrTaxLEzSyOve+up5nVafgnAZKya0xLKSFplqnlxjAjGtr7XWi4Z4RfVOuBkjaQHykXt4DqVF4/wAfijb/APl0PdgiP8VK03dPL0J38f8AhbU77YX663tjHOEdQ90D3GOOZxp3m7TkB7p+S77whi7auGOYEXc0CRo+5IOYXz0Fc8N8T1NC8ugeMriM8b2iRj7fvZWwtXX00w6KtxN1lleGPabS1FmVH8NKbC7jnhcfPb19602JODmgggggEFpDgQoiMlPJ/wAvcPluE9WS2Cr8OJF09Wu096rO2cTPiTh0tyVYveqKiflcVYvl0RPsUnp69/eCmscLKoa4k3U+N2iVlUT6d3eHmEJiN1iPMIWct4lj8HqTr/UVoY3khUWH02V72/hlePitFTxaK7e3PTXjGKXCxeMjUhjFLWsPUJRCZqpMjHvtfIxzrDmbDkkvGe44xWSKmljpjeqkYBG0EMLAebr+V188VTHseWyAh4JzB1wbrrWM4k+pk7VgbmDQ0sBLLt8+qqcWwyKdlpWWe0ENkbo8fqpjkyW8cG169ubk33spOHSOE0Rbq4Sxlv8AVcWSK2ldC8scOR0PLM3qn8AaXVUIaMzu0DgOttfyXRXthMY6JxRQSRy0czi5wlgbBJI8lzjI2+pPkfgpWAcPmc9pJpDclrQcjpfXYK34okdLT03Ls2uIy5dRLbT81c4VIWUsbCzs3NYc7jpZl/0UfHFuWdht8kxxRkstx/xeyjpm0lI3spZGub3dOxi5EjqTrr5ri99/3dXHFeKfSquaUfYLskQ/yhoP19VTFaWz1DAZidrea9a7ZN5t0qMbqTPsctDgPFtVSWax+aPeGS72W8Onos2CjPuUyzXdOD+LqascIyeyndyieftn+U7rXVENwvmHDqtzJopGkgxyxva4d2xBX1W5ml/AJSjxiFVBT6p90SkhouhwCnR44ZZTp7sktpSnFBxBDW8vRCUzmB1IQoVCCKENmlP4pHO9+qsookqrbZ4P4gPelsKczsCKxEgMSrLzOkOlCMUcJTEzjY252Nr6C6S+cKJUyZmubs4FptponhTZymUOe+STNleXuLm6BodfayQJ3O0d+wkVj2l8jGv70MskRcLauBsU1HJsTqPS4XLb29KmeMIuN4aJ2WGjm3yO6FZ7hC8eI04eLETFjgdLEgha8yqmq8OP0qCpj+7PCZAOdgRqtuG+TksPyOPY2HcKeFpHIWuNNCLjdZD2oY19HpDGw2fVExNI0tH94+7T1W0gFmA+F1w/2rYr21b2QPdpWBnX6w6n8vcu2ZzZcMMW5MuNz4D5pUrthzPySWiyyWHDZLvZIJt5lNPffTbdIHs++wSb5j4JvLfnoOnJKvsEBacPURqaungaL9rNG021s2+p9BdfUsjtFwj2L0gNbJMRpTwG3g9xt8rrtEtQlKZnD+fVJkkUUSIe5JOn2yp4PUBjtVKjRJwl04u9vndCXh7buJ6D4r1Rb21rHR3ER3Mw+6b+igNqVcPaCCDyIII8FV/RcpI6fJOsptE7pp0rik6lSxD4I7JNOSidmVBx2qFNTTzn/oxPePF1tB77K5yLFe2Gr7LC5ADYzywwjyvmP/qmMcOgxmSJ5cTnEji+RrvvE8z5rTUVbFKMzD0u0gtLCsDJfcrZ8O4cPoocHd+Ul1tso0AWXLWPbr4LTuLYTW5nbnzWo4f4LqKuAT52wNkGaISMMrnN62uLLn1fVPiY7TXVuX7Qv5rtPBXG1DPRQ3njikhhZHNFLI2BzHNFt9tEqR1qua8x0xlfxdWYUX0VXGJ3tLTBNnLM1OeYPXwPvXKMTrHSyyzP+1LI+Q+ZN1s/avxHDXVzTAc8VPEIRKOUjrkkjw1WGmZm/JdOzjj/AGbYd9ylXTYNtEolKDJmfokRfslNvN3AKQ1gPog3oIO6WGBIMSA0oJ1z2LUn1NVL+OaOMHyF/wD6XRntWX9lFNkw2I2sZXyyH/dYfALYOCGc+zDGIe1PsCJGpEiMOqlRuUct1T9PHmcGjcj3Ik4XOHssy/4tfReKS1thYbAAIWMt4KTcrN04vEGYskOCdc2yQQqIzZfO/tb4tdWVboGXFPRPfE0fjmGjnfkP+V9GZV8lY+c9XUlos01U5bfpmKqE4rYoHSODWAuc4gADXVdJw9rOwiby7NjWaEs1t1VDwW+KOSpke0O7HDqyVjTvLlsPmU23FxJGWbW1B5WUcsdQ6OCcmVnxLVsjiIcA4uBynQG/isZAdLka66+CKqUuOpJDSbAklNhyrjrkI5b+UpWZeFyZDkXutdYFSMzXPIgXsmc6kApD4w7XlpzSNEYLkkbKbG7TxCiNaWHQXvvrqE/FKPIpQclmQoDidBvblrqlEhXfBGG/ScQporXAlEr/APxt7x+Vk0u6cOU/0elp4bWMUEbXD+a2vxup75kjJr70hzUM0yJ6U96iscvJJEAsu1VxhEFhnO+jfJVOHU5lfb7o1efBaZrQBYchoPJRef0046/spCELNqEIQgPHC6ZIT6S5t04JU8Q1LoaSqlZ9uGlnlZv3g0kL5Ke8k6nU31Ouq+wauBr2Pjfq2Rjo3Dq0ixXyLjuHvpamenkFnwSujN7i4B0PqLFXBJuAFxlfG0i81LVwtBsMzjG6w9TYJVJw7UtBMzewYPtPkIvbwG/y8VTh+48D01U2XEqif6kFzs21y9zgPHoqyJ9iJmPSNidWwuayIAMiDmh5AzyEm5JPyUcO/LoFHYE8GaXukCw5ONemA5KugjuZKL726Ji6U0p6MSBbRMvHMEeR5aIzfvwXpcLH0TJ41+3TfwXVvYdhN3VNYRoxopoz/MdXfAD3rk17W9x819C+yOiMOFRlwsZ5ZpwDp3SbD4BIT6ans03K1PhIkCGaLZEcLnuDWi5PyUiGAuNgNT8leUVIIx1cebkrWw610qipRE3KPNx6lSEIWTeAhCEAIQhACEIQCXtuuZe032cDED9IhcI6prQ0l1xHOwbO6HxXT14Rf93TicKYfMmHey/E3vIexkAaSO0lla8HyDblavEODafC8Oq6jMZak0skHam7GtL+73R67rsVTQX1boeh5Lm3tmc6LDSxwt2tRCzztd35K4nUTrgTWWSrfvxXpXqaiC1JKcQQgEAr0FJc3okh/VAOkr26QClAoB2mgdK9kbBd0kjGMaNbuOgX1XTwCKKKIcoYo4xboBZcY9ieBRz1MtVJqaLszEwi/wBY69nelj712xjHPNgCU0W/gjanYqVzzpoNyVNp6Kw72vgOSlgKZt/Din9NU8DWCw9TuU8hCzaBCEIAQhCAEIQgBCEIAQhCAEzVU0crCyVjZGOFnRyMErXDxBQhAYHHvY/hlTd0IfSPOv1Ds8d/6D+Vlg8W9iNfHc080VQ0cg4uo5D6G4/uQhPZLGUr/Z9i8N89BKbbwtFaP7LqmqMHqo/8SmmZ4SQSR/MLxCuJ0jBpJf8Atv8A9jk5DgtVLpHTTPP+XBLJ8ghCYW+H+zvGJrBlBKAd5miiFv8AUQtdhHsPr5LGpnip27hpdWyD0Fh/chCibSeOqcEcA02FNk7OSSZ8+TtXy5WtuL2sBy5ncrXNaBoNPLRCEtPHqEISAQhCAEIQgBCEID//2Q==", 
                    width=100)
        with col2:
            st.markdown("**Kavin N R**")
            st.markdown("AI Professional")
            st.markdown("[LinkedIn Profile](https://www.linkedin.com/in/kavinnr/)")
        st.markdown("---")

# Handle user input
user_input = st.chat_input("Your answer")
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    response = requests.post("http://localhost:8000/chat", json={
        "message": user_input,
        "chat_history": st.session_state.chat_history
    })
    bot_reply = response.json()["reply"]

    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

    if st.session_state.question_index < len(questions):
        st.session_state.question_index += 1