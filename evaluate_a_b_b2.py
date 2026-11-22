import urllib.request
import json
import time

SAMPLES = [
    # --- HINDI ---
    {
        "id": "HI-01",
        "lang": "hindi",
        "title": "ISRO Satellite Launch (Science News)",
        "source": "भारतीय अंतरिक्ष अनुसंधान संगठन (ISRO) ने श्रीहरिकोटा के सतीश धवन अंतरिक्ष केंद्र से एक नया संचार उपग्रह सफलतापूर्वक लॉन्च किया। वैज्ञानिकों ने इस मिशन को ऐतिहासिक सफलता बताया। यह उपग्रह अगले 10 वर्षों तक देश के दूरदराज के क्षेत्रों में हाई-स्पीड इंटरनेट और दूरसंचार सेवाएं प्रदान करेगा।"
    },
    {
        "id": "HI-02",
        "lang": "hindi",
        "title": "GST Revenue ₹20.18L Cr (Economic Data)",
        "source": "वित्त मंत्रालय ने शुक्रवार को घोषणा की कि वित्त वर्ष 2024-25 में कुल सकल GST संग्रह ₹20.18 लाख करोड़ तक पहुंच गया, जो पिछले वर्ष के ₹18.10 लाख करोड़ से 11.5 प्रतिशत अधिक है। हालांकि, अंतिम लेखापरीक्षित आंकड़े 31 मार्च के बाद जारी किए जाएंगे।"
    },
    {
        "id": "HI-03",
        "lang": "hindi",
        "title": "Health Advisory (Uncertainty & Advisory)",
        "source": "स्वास्थ्य विभाग ने चेतावनी दी है कि सर्दियों के दौरान मौसमी इन्फ्लूएंजा के मामलों में वृद्धि होने की संभावना है, हालांकि किसी नए घातक वेरिएंट की पुष्टि नहीं हुई है। अधिकारियों ने वरिष्ठ नागरिकों को सावधानी बरतने और भीड़भाड़ में मास्क पहनने की सलाह दी है, परंतु किसी प्रकार का लॉकडाउन या यात्रा प्रतिबंध लागू नहीं किया गया है।"
    },

    # --- HINGLISH ---
    {
        "id": "HG-01",
        "lang": "hinglish",
        "title": "FreshRoute Startup Launch (Business & Metrics)",
        "source": "Bengaluru-based startup FreshRoute ne 19 November 2026 ko apni grocery delivery service launch ki. Company ke founder Rohan Mehta ne bataya ki initially service Bengaluru ke 7 areas mein available hogi. Startup ne ab tak 42 local farmers aur 18 delivery partners ke saath agreements sign kiye hain. Customers ko order place karne ke 12 se 24 hours ke andar delivery provide karne ka target rakha gaya hai. Company ka aim hai ki first four months mein 3,500 customers tak reach kiya ja sake. Rohan ne kaha ki company abhi doosre cities mein expansion plan finalize nahi kar rahi hai. Delivery charges aur minimum order value ki details next week announce ki jayengi."
    },
    {
        "id": "HG-02",
        "lang": "hinglish",
        "title": "Study Schedule Planning (Purpose vs Outcome)",
        "source": "Many students apna daily study schedule plan karte hain taaki important assignment deadlines miss na ho. Lekin classes aur projects ke beech time manage karna kaafi challenging hota hai."
    },
    {
        "id": "HG-03",
        "lang": "hinglish",
        "title": "Placement Talk Relocation (Negation & Venue)",
        "source": "Karan: Guys kal subah 10 baje college auditorium mein placement talk hai. Simran: Par sunne mein aaya tha ki placement drive cancel ho gaya hai? Karan: Nahi, drive cancel nahi hua hai, bas venue change ho gaya hai pehle seminar hall tha ab auditorium hai."
    },

    # --- ENGLISH ---
    {
        "id": "EN-01",
        "lang": "english",
        "title": "RBI Repo Rate 6.5% (Monetary Policy)",
        "source": "The Reserve Bank of India on Friday kept the benchmark repo rate unchanged at 6.5 percent for the eighth consecutive monetary policy review. Governor Shaktikanta Das stated that while headline inflation has moderated to 4.8 percent, food price volatility remains a significant risk."
    },
    {
        "id": "EN-02",
        "lang": "english",
        "title": "NexTech $450M Hub (Condition & Timeline)",
        "source": "NexTech Corporation announced plans to invest $450 million in a new semiconductor design facility in Bengaluru, subject to central government subsidies. The management clarified that while land acquisition is complete, commercial production will not commence before early 2027."
    },
    {
        "id": "EN-03",
        "lang": "english",
        "title": "Oxford Parkinson's Biomarker (Scientific Caution)",
        "source": "Medical researchers at Oxford University have identified a blood biomarker that may detect early signs of Parkinson's disease up to seven years before clinical symptoms emerge. However, the study authors emphasized that the findings are preliminary and require validation across larger, diverse patient cohorts before clinical deployment."
    }
]

def run_evaluation():
    url = "http://localhost:8000/api/summarize_all"
    full_results = []

    print(f"Running A vs B vs B2 Comparative Benchmark across {len(SAMPLES)} samples...\n")

    for i, item in enumerate(SAMPLES, 1):
        print(f"[{i}/{len(SAMPLES)}] Testing {item['id']}: {item['title']} ({item['lang']})...")
        payload = json.dumps({
            "source_text": item["source"],
            "language": item["lang"],
            "summary_length": "medium",
            "include_b2": True
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                elapsed = round(time.time() - t0, 2)
                res = {
                    "id": item["id"],
                    "lang": item["lang"],
                    "title": item["title"],
                    "source": item["source"],
                    "elapsed_sec": elapsed,
                    "condition_A": data.get("condition_A"),
                    "condition_B": data.get("condition_B"),
                    "condition_B2": data.get("condition_B2"),
                }
                full_results.append(res)
                print(f"    Done in {elapsed}s | A: Supp={data['condition_A']['support_rate']}%, Contra={data['condition_A']['contradiction_rate']}% | B: Supp={data['condition_B']['support_rate']}%, Contra={data['condition_B']['contradiction_rate']}% | B2: Supp={data['condition_B2']['support_rate']}%, Contra={data['condition_B2']['contradiction_rate']}%")
        except Exception as e:
            print(f"    Error: {e}")

    with open("/Users/aarushi/factIndic/a_b_b2_comparison_results.json", "w", encoding="utf-8") as f:
        json.dump(full_results, f, indent=2, ensure_ascii=False)
    print("\nBenchmark completed! Saved to /Users/aarushi/factIndic/a_b_b2_comparison_results.json")

if __name__ == "__main__":
    run_evaluation()
