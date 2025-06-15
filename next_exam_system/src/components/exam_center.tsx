'use client';

import {useState, useEffect} from 'react';

interface Question {
    id: number;
    text: string;
}

interface ExamCenterProps {
    questions: Question[];
}

export default function ExamCenter({questions}: ExamCenterProps) {
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [answers, setAnswers] = useState<Record<number, string>>({});
    const [timeLeft, setTimeLeft] = useState(30*60);
    const [examStarted, setExamStarted] = useState(false);

    useEffect(() => {
        if (!examStarted) return;

        const timerId = setTimeout(() => {
            setTimeLeft(timeLeft - 1);
        }, 1000);

        return () => clearTimeout(timerId);
    }, [timeLeft, examStarted]);

    const handleAnswerChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setAnswers({
            ...answers,
            [questions[currentQuestionIndex].id]: e.target.value,
        });
    };

    // ✅ Auto-save function to backend (placeholder logic)
    const saveAnswerToBackend = async () => {
        const questionId = questions[currentQuestionIndex].id;
        const answerText = answers[questionId] || '';

        try {
            // Replace with your real API call (e.g. fetch/axios/post)
            console.log(`Saving answer for question ${questionId}:`, answerText);
            // await fetch('/api/saveAnswer', { method: 'POST', body: JSON.stringify({ questionId, answerText }) });
        } catch (error) {
            console.error('Failed to save answer:', error);
        }
    };

    const goNext = async () => {
        await saveAnswerToBackend();
        if (currentQuestionIndex < questions.length - 1) {
            setCurrentQuestionIndex(currentQuestionIndex + 1);
        } else {
            alert('You have reached the last question.');
        }
    };

    const goPrev = async () => {
        await saveAnswerToBackend();
        if (currentQuestionIndex > 0) {
            setCurrentQuestionIndex(currentQuestionIndex - 1);
        }
    };

    const startExam = () => {
        setExamStarted(true);
        if (document.documentElement.requestFullscreen) {
            document.documentElement.requestFullscreen();
        }
    };

    const submitExam = async () => {
        await saveAnswerToBackend(); // Save last answer
        alert('Submitting your exam now!');
        // TODO: Submit all answers to backend
        setExamStarted(false);
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
    };

    const formatTime = (seconds: number) => {
        const m = Math.floor(seconds / 60).toString().padStart(2, '0');
        const s = (seconds % 60).toString().padStart(2, '0');
        return `${m}:${s}`;
    };

    if (!examStarted) {
        return (
            <div className="max-w-xl mx-auto p-8 text-center">
                <h1 className="text-3xl font-bold mb-6">Ready to start your exam?</h1>
                <button
                    onClick={startExam}
                    className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                    Start Exam
                </button>
            </div>
        );
    }

    return (
        <div className="max-w-3xl mx-auto p-6 bg-white rounded shadow-lg">
            <div className="flex justify-between mb-4">
                <div className="font-mono text-red-950">Time Left: {formatTime(timeLeft)}</div>
                <button
                    onClick={submitExam}
                    className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                >
                    Submit Exam
                </button>
            </div>

            <div className="mb-4">
                <h2 className="text-xl font-semibold mb-2 text-black">
                    Question {currentQuestionIndex + 1} of {questions.length}
                </h2>
                <p className="mb-4 text-black">{questions[currentQuestionIndex].text}</p>

                <textarea
                    className="w-full border border-gray-300 rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
                    rows={6}
                    value={answers[questions[currentQuestionIndex].id] || ''}
                    onChange={handleAnswerChange}
                    placeholder="Type your answer here..."
                />
            </div>

            <div className="flex justify-between">
                <button
                    onClick={goPrev}
                    disabled={currentQuestionIndex === 0}
                    className="px-4 py-2 bg-gray-600 rounded disabled:opacity-50"
                >
                    Previous
                </button>
                <button
                    onClick={goNext}
                    disabled={currentQuestionIndex === questions.length - 1}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                >
                    Next
                </button>
            </div>
        </div>
    );
}
