import ExamCenter from '@/components/exam_center';
import { NextRequest, NextResponse } from 'next/server';

function decodeURIComponentSafe(str: string) {
    try {
        return decodeURIComponent(str);
    } catch {
        return str;
    }
}

interface Question {
    id: number;
    text: string;
    marks: number;
}

searchParams{
    key: string[];
}

export default function Page(searchParams:) {
    const raw = searchParams.data;
    let questions: Question[] = [];

    if (raw) {
        try {
            const decoded = decodeURIComponentSafe(raw);
            questions = JSON.parse(decoded);
        } catch (e) {
            console.error('Failed to decode or parse questions:', e);
        }
    }

    return <ExamCenter questions={questions} />;
}
