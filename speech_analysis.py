import streamlit as st
from collections import Counter
from docx import Document
import textstat
import language_tool_python
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from textblob import TextBlob
import nltk

nltk.download('punkt')

# Function to read transcript from DOCX file
def read_transcript(docx_path):
    doc = Document(docx_path)
    transcript = []
    for para in doc.paragraphs:
        transcript.append(para.text)
    return transcript

# Function to extract speaker text with more robust handling
def extract_speaker_text(transcript, speaker):
    capture = False
    speaker_text = []
    for line in transcript:
        if line.startswith(speaker):
            capture = True
        elif capture and line.strip() == "":
            capture = False
        if capture and not line.startswith(speaker):
            speaker_text.append(line.strip())
    return " ".join(speaker_text)

# Function to calculate vocabulary diversity
def calculate_vocabulary_diversity(text):
    words = text.split()
    unique_words = set(words)
    return len(unique_words) / len(words) if words else 0

# Function to calculate sentiment using TextBlob
def analyze_tone(text):
    analysis = TextBlob(text)
    score = analysis.sentiment.polarity
    if score > 0:
        tone = 'Positive'
    elif score < 0:
        tone = 'Negative'
    else:
        tone = 'Neutral'
    return (tone, score)

# Function to calculate question frequency
def calculate_question_frequency(sentences):
    question_sentences = [sentence for sentence in sentences if sentence.strip().endswith('?')]
    return len(question_sentences)

# Function to analyze text
def analyze_text(text):
    sentences = nltk.sent_tokenize(text)
    words = nltk.word_tokenize(text)
    filler_words = [word for word in words if word.lower() in ["uh", "um", "you know", "like", "er", "ah", "so", "actually", "basically", "right", "well", "you see", "i mean", "sort of"]]
    word_freq = Counter(words)
    filler_freq = Counter(filler_words)
    avg_sentence_length = sum(len(sentence.split()) for sentence in sentences) / len(sentences) if sentences else 0

    # Calculate additional metrics
    total_words = len(words)
    total_sentences = len(sentences)
    vocab_diversity = calculate_vocabulary_diversity(text)
    clarity = textstat.flesch_reading_ease(text)
    tone = analyze_tone(text)
    question_freq = calculate_question_frequency(sentences)

    # Get top 10 most common words
    most_common_words = dict(word_freq.most_common(10))

    return {
        "total_words": total_words,
        "total_sentences": total_sentences,
        "most_common_words": most_common_words,
        "filler_freq": filler_freq,
        "avg_sentence_length": avg_sentence_length,
        "clarity": clarity,
        "tone": tone,
        "vocab_diversity": vocab_diversity,
        "question_freq": question_freq
    }

# Function to correct grammar using language_tool_python
def correct_grammar(text):
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)

    # Filter grammar matches to exclude less critical errors
    significant_errors = [match for match in matches if match.ruleId not in [
        'UPPERCASE_SENTENCE_START', 'PUNCTUATION_PARAGRAPH_END',
        'EN_A_VS_AN', 'AGREEMENT_SENT_START', 'MORFOLOGIK_RULE_EN_US']]

    corrected_text = tool.correct(text)

    # Collect detailed information about each error
    detailed_errors = []
    for match in significant_errors:
        # Extract the exact mistake from the text
        mistake = text[match.offset:match.offset + match.errorLength]
        
        error_details = {
            "Sentence": match.context,
            "Mistake": mistake,
            "Suggestion": match.replacements
        }
        detailed_errors.append(error_details)

    return corrected_text, detailed_errors


# Function to summarize text using Sumy
def summarize_text(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary = summarizer(parser.document, 3)  # Summarize to 3 sentences
    return " ".join([str(sentence) for sentence in summary])


def give_analysis(file,speaker_names):
    transcript = read_transcript(file)
    if speaker_names:
        # Dictionary to store analytics for each speaker
        analytics = {}

        for selected_speaker in speaker_names:
            print(f"Analyzing for {selected_speaker}")
            speaker_text = extract_speaker_text(transcript, selected_speaker)

            # Analyze text for the speaker
            analysis = analyze_text(speaker_text, duration_minutes=None)  # Set duration_minutes as None since it's not used

            # Correct grammar for the speaker
            corrected_text, grammar_matches = correct_grammar(speaker_text)

            # Summarize text for the speaker
            summary = summarize_text(corrected_text)

            # Store analytics in the dictionary
            analytics[selected_speaker] = {
                "Total Words Spoken": analysis["total_words"],
                "Total Sentences Spoken": analysis["total_sentences"],
                "Most Common Words": analysis["most_common_words"],
                "Filler Frequency": analysis["filler_freq"],
                "Average Sentence Length": analysis["avg_sentence_length"],
                "Clarity": analysis["clarity"],
                "Tone": analysis["tone"],
                "Summary": summary,
                "Grammar Issues": grammar_matches,
                "Vocabulary Diversity": analysis["vocab_diversity"],
                "Question Frequency": analysis["question_freq"]
            }
    return analytics