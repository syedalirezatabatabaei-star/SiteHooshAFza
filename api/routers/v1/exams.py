from fastapi import APIRouter, Depends, HTTPException, status
from django.utils import timezone
from django.db import transaction

from deps import get_current_user
from schemas.v1.exams import (
    ExamListResponse, ExamDetailResponse, ExamSubmitRequest, ExamResultResponse,
    QuestionResponse, ChoiceResponse,
)
from apps.exams.models import Exam, ExamAttempt, ExamAnswer, Question, Choice
from apps.enrollments.models import Enrollment

router = APIRouter()


@router.get('/attempts/{attempt_id}')
def attempt_result(attempt_id: int, user=Depends(get_current_user)):
    try:
        attempt = ExamAttempt.objects.get(pk=attempt_id, student=user)
    except ExamAttempt.DoesNotExist:
        raise HTTPException(status_code=404, detail='تلاش آزمون یافت نشد')
    return {'id': attempt.id, 'exam_id': attempt.exam_id, 'score': attempt.score,
            'passed': attempt.passed, 'started_at': attempt.started_at,
            'completed_at': attempt.completed_at}


@router.get('/{exam_id}/attempts')
def list_attempts(exam_id: int, user=Depends(get_current_user)):
    return [{'id': attempt.id, 'exam_id': attempt.exam_id, 'score': attempt.score,
             'passed': attempt.passed, 'started_at': attempt.started_at,
             'completed_at': attempt.completed_at}
            for attempt in ExamAttempt.objects.filter(exam_id=exam_id, student=user)]


@router.get('')
def list_exams(
    course_id: int = None,
    user=Depends(get_current_user),
):
    """لیست آزمون‌های دوره‌های ثبت‌نام شده"""
    enrolled_course_ids = Enrollment.objects.filter(
        student=user, status='ACTIVE'
    ).values_list('course_id', flat=True)

    qs = Exam.objects.filter(is_active=True, course_id__in=enrolled_course_ids)

    if course_id:
        qs = qs.filter(course_id=course_id)

    return [ExamListResponse(
        id=e.id, title=e.title, description=e.description,
        duration_minutes=e.duration_minutes, passing_score=e.passing_score,
        question_count=e.question_count, course_id=e.course_id,
    ) for e in qs]


@router.get('/{exam_id}')
def get_exam(exam_id: int, user=Depends(get_current_user)):
    """جزئیات آزمون با سؤالات"""
    try:
        exam = Exam.objects.get(pk=exam_id, is_active=True)
    except Exam.DoesNotExist:
        raise HTTPException(status_code=404, detail='آزمون یافت نشد')

    # Check enrollment
    if not Enrollment.objects.filter(student=user, course=exam.course, status='ACTIVE').exists():
        raise HTTPException(status_code=403, detail='شما در این دوره ثبت‌نام نکرده‌اید')

    questions = []
    for q in exam.questions.prefetch_related('choices').order_by('order'):
        choices = [ChoiceResponse(id=c.id, text=c.text) for c in q.choices.all()]
        questions.append(QuestionResponse(
            id=q.id, text=q.text, score=q.score, order=q.order, choices=choices,
        ))

    return ExamDetailResponse(
        id=exam.id, title=exam.title, description=exam.description,
        duration_minutes=exam.duration_minutes, passing_score=exam.passing_score,
        questions=questions, total_score=exam.total_score,
    )


@router.post('/{exam_id}/start')
def start_exam(exam_id: int, user=Depends(get_current_user)):
    """شروع آزمون"""
    try:
        exam = Exam.objects.get(pk=exam_id, is_active=True)
    except Exam.DoesNotExist:
        raise HTTPException(status_code=404, detail='آزمون یافت نشد')

    if not Enrollment.objects.filter(student=user, course=exam.course, status='ACTIVE').exists():
        raise HTTPException(status_code=403, detail='شما در این دوره ثبت‌نام نکرده‌اید')

    # Check for incomplete attempt
    incomplete = ExamAttempt.objects.filter(
        exam=exam, student=user, completed_at__isnull=True,
    ).first()

    if incomplete:
        # Check if expired
        elapsed = (timezone.now() - incomplete.started_at).total_seconds() / 60
        if elapsed > exam.duration_minutes:
            incomplete.completed_at = timezone.now()
            incomplete.score = 0
            incomplete.passed = False
            incomplete.save()
        else:
            return {'attempt_id': incomplete.id, 'duration_remaining': exam.duration_minutes - int(elapsed)}

    attempt = ExamAttempt.objects.create(exam=exam, student=user)
    return {'attempt_id': attempt.id, 'duration_minutes': exam.duration_minutes}


@router.post('/{exam_id}/submit', response_model=ExamResultResponse)
def submit_exam(
    exam_id: int,
    data: ExamSubmitRequest,
    user=Depends(get_current_user),
):
    """ارسال پاسخ‌های آزمون"""
    try:
        exam = Exam.objects.get(pk=exam_id, is_active=True)
    except Exam.DoesNotExist:
        raise HTTPException(status_code=404, detail='آزمون یافت نشد')

    attempt = ExamAttempt.objects.filter(
        exam=exam, student=user, completed_at__isnull=True,
    ).first()

    if not attempt:
        raise HTTPException(status_code=400, detail='تلاش فعالی برای این آزمون وجود ندارد')
    if attempt.is_expired:
        raise HTTPException(status_code=400, detail='زمان آزمون به پایان رسیده است')
    question_ids = [answer.question_id for answer in data.answers]
    if len(question_ids) != len(set(question_ids)):
        raise HTTPException(status_code=422, detail='برای هر سؤال فقط یک پاسخ مجاز است')

    with transaction.atomic():
        total_score = exam.total_score
        earned_score = 0

        for answer_data in data.answers:
            try:
                question = Question.objects.get(pk=answer_data.question_id, exam=exam)
                choice = question.choices.get(pk=answer_data.choice_id)
            except (Question.DoesNotExist, Choice.DoesNotExist):
                continue

            ExamAnswer.objects.create(
                attempt=attempt,
                question=question,
                choice=choice,
            )
            if choice.is_correct:
                earned_score += question.score

        score = round((earned_score / total_score) * 100, 2) if total_score > 0 else 0
        passed = score >= float(exam.passing_score)

        attempt.completed_at = timezone.now()
        attempt.score = score
        attempt.passed = passed
        attempt.save()

        # Check certificate eligibility
        if passed:
            from apps.certificates.models import Certificate
            enrollment = Enrollment.objects.filter(student=user, course=exam.course).first()
            if enrollment and enrollment.progress >= 70:
                Certificate.objects.get_or_create(
                    student=user,
                    course=exam.course,
                    defaults={'status': 'ISSUED'},
                )

    return ExamResultResponse(
        score=attempt.score,
        total_score=total_score,
        passed=passed,
        passing_score=exam.passing_score,
    )
