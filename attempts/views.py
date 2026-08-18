from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Attempt, Answer
from .serializers import AttemptSerializer

from quizzes.models import Quiz
from questions.models import Question, Option


class StartQuizView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, quiz_id):

        quiz = get_object_or_404(
            Quiz,
            id=quiz_id
        )

        # Only published quizzes can be attempted
        if quiz.status != "Published":
            return Response(
                {
                    "error": "This quiz is not available."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check maximum attempts
        previous_attempts = Attempt.objects.filter(
            student=request.user,
            quiz=quiz
        ).exclude(
            status="IN_PROGRESS"
        ).count()

        if previous_attempts >= quiz.max_attempts:
            return Response(
                {
                    "error": "Maximum attempts reached."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for an existing active attempt
        active_attempt = Attempt.objects.filter(
            student=request.user,
            quiz=quiz,
            status="IN_PROGRESS"
        ).first()

        if active_attempt:
            return Response(
                AttemptSerializer(active_attempt).data,
                status=status.HTTP_200_OK
            )

        # Create a new attempt
        attempt = Attempt.objects.create(
            student=request.user,
            quiz=quiz
        )

        return Response(
            AttemptSerializer(attempt).data,
            status=status.HTTP_201_CREATED
        )


class SubmitQuizView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, attempt_id):

        attempt = get_object_or_404(
            Attempt,
            id=attempt_id,
            student=request.user
        )

        # Check whether the attempt is already completed
        if attempt.status != "IN_PROGRESS":
            return Response(
                {
                    "error": (
                        "This attempt has already "
                        "been completed."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate quiz expiry time
        expiry_time = (
            attempt.started_at
            + timedelta(minutes=attempt.quiz.duration)
        )

        # Check whether quiz time has expired
        if timezone.now() > expiry_time:

            attempt.status = "FAILED"
            attempt.completed_at = timezone.now()

            attempt.save()

            return Response(
                {
                    "error": "Quiz time has expired.",
                    "status": "FAILED"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get submitted answers
        answers = request.data.get(
            "answers",
            []
        )

        correct = 0
        incorrect = 0
        unanswered = 0
        obtained_marks = 0
        total_marks = 0

        # Get all questions belonging to this quiz
        questions = Question.objects.filter(
            quiz=attempt.quiz
        )

        for question in questions:

            total_marks += question.marks

            # Find submitted answer for this question
            submitted_answer = next(
                (
                    answer
                    for answer in answers
                    if answer.get("question_id") == question.id
                ),
                None
            )

            # No answer submitted
            if not submitted_answer:
                unanswered += 1
                continue

            option_id = submitted_answer.get(
                "option_id"
            )

            # Make sure selected option belongs
            # to this question
            option = Option.objects.filter(
                id=option_id,
                question=question
            ).first()

            if not option:
                return Response(
                    {
                        "error": (
                            f"Invalid option for question "
                            f"{question.id}."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check answer on backend
            is_correct = option.is_correct

            # Save submitted answer
            Answer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=option,
                is_correct=is_correct
            )

            if is_correct:
                correct += 1
                obtained_marks += question.marks
            else:
                incorrect += 1

        # Calculate percentage
        if total_marks > 0:
            percentage = (
                obtained_marks / total_marks
            ) * 100
        else:
            percentage = 0

        # Determine pass/fail
        if percentage >= attempt.quiz.passing_percentage:
            result_status = "PASSED"
        else:
            result_status = "FAILED"

        # Completion time
        end_time = timezone.now()

        time_taken = int(
            (
                end_time - attempt.started_at
            ).total_seconds()
        )

        # Update attempt
        attempt.score = obtained_marks
        attempt.percentage = percentage
        attempt.correct_answers = correct
        attempt.incorrect_answers = incorrect
        attempt.unanswered = unanswered
        attempt.time_taken = time_taken
        attempt.status = result_status
        attempt.completed_at = end_time

        attempt.save()

        return Response(
            AttemptSerializer(attempt).data,
            status=status.HTTP_200_OK
        )


class AttemptResultView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, attempt_id):

        # Student can only access their own attempt
        attempt = get_object_or_404(
            Attempt,
            id=attempt_id,
            student=request.user
        )

        # Don't allow result before completion
        if attempt.status == "IN_PROGRESS":
            return Response(
                {
                    "error": (
                        "Quiz attempt is not completed yet."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "attempt_id": attempt.id,
                "quiz_id": attempt.quiz.id,
                "quiz_title": attempt.quiz.title,
                "score": attempt.score,
                "percentage": attempt.percentage,
                "correct_answers": attempt.correct_answers,
                "incorrect_answers": attempt.incorrect_answers,
                "unanswered": attempt.unanswered,
                "time_taken": attempt.time_taken,
                "status": attempt.status,
                "started_at": attempt.started_at,
                "completed_at": attempt.completed_at,
            },
            status=status.HTTP_200_OK
        )


class AttemptHistoryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # Get only the logged-in student's attempts
        attempts = Attempt.objects.filter(
            student=request.user
        ).exclude(
            status="IN_PROGRESS"
        ).select_related(
            "quiz"
        ).order_by(
            "-completed_at"
        )

        history = []

        for attempt in attempts:

            history.append(
                {
                    "attempt_id": attempt.id,
                    "quiz_id": attempt.quiz.id,
                    "quiz_title": attempt.quiz.title,
                    "score": attempt.score,
                    "percentage": attempt.percentage,
                    "correct_answers": (
                        attempt.correct_answers
                    ),
                    "incorrect_answers": (
                        attempt.incorrect_answers
                    ),
                    "unanswered": attempt.unanswered,
                    "time_taken": attempt.time_taken,
                    "status": attempt.status,
                    "completed_at": (
                        attempt.completed_at
                    ),
                }
            )

        return Response(
            history,
            status=status.HTTP_200_OK
        )


class AnswerReviewView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, attempt_id):

        # Student can only review their own attempt
        attempt = get_object_or_404(
            Attempt,
            id=attempt_id,
            student=request.user
        )

        # Only completed attempts can be reviewed
        if attempt.status == "IN_PROGRESS":
            return Response(
                {
                    "error": (
                        "Quiz attempt is not completed yet."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get answers for this attempt
        answers = Answer.objects.filter(
            attempt=attempt
        ).select_related(
            "question",
            "selected_option"
        )

        review = []

        for answer in answers:

            # Find the correct option
            correct_option = Option.objects.filter(
                question=answer.question,
                is_correct=True
            ).first()

            review.append(
                {
                    "question_id": answer.question.id,

                    "question": (
                        answer.question.question_text
                    ),

                    "selected_option": (
                        answer.selected_option.option_text
                        if answer.selected_option
                        else None
                    ),

                    "correct_option": (
                        correct_option.option_text
                        if correct_option
                        else None
                    ),

                    "is_correct": answer.is_correct,

                    "explanation": (
                        answer.question.explanation
                    ),

                    "marks": answer.question.marks,
                }
            )

        return Response(
            {
                "attempt_id": attempt.id,
                "quiz_id": attempt.quiz.id,
                "quiz_title": attempt.quiz.title,
                "review": review,
            },
            status=status.HTTP_200_OK
        )


class AdminAttemptListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # Only admin users can access this endpoint
        if request.user.role != "ADMIN":
            return Response(
                {
                    "error": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Get all completed attempts
        attempts = Attempt.objects.filter(
            status__in=[
                "PASSED",
                "FAILED"
            ]
        ).select_related(
            "student",
            "quiz"
        ).order_by(
            "-completed_at"
        )

        data = []

        for attempt in attempts:

            data.append(
                {
                    "attempt_id": attempt.id,

                    "student_id": (
                        attempt.student.id
                    ),

                    "student_username": (
                        attempt.student.username
                    ),

                    "quiz_id": (
                        attempt.quiz.id
                    ),

                    "quiz_title": (
                        attempt.quiz.title
                    ),

                    "score": attempt.score,

                    "percentage": (
                        attempt.percentage
                    ),

                    "correct_answers": (
                        attempt.correct_answers
                    ),

                    "incorrect_answers": (
                        attempt.incorrect_answers
                    ),

                    "unanswered": (
                        attempt.unanswered
                    ),

                    "time_taken": (
                        attempt.time_taken
                    ),

                    "status": attempt.status,

                    "started_at": (
                        attempt.started_at
                    ),

                    "completed_at": (
                        attempt.completed_at
                    ),
                }
            )

        return Response(
            data,
            status=status.HTTP_200_OK
        )


class AdminAttemptDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, attempt_id):

        # Only admin users can access this endpoint
        if request.user.role != "ADMIN":
            return Response(
                {
                    "error": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        attempt = get_object_or_404(
            Attempt.objects.select_related(
                "student",
                "quiz"
            ),
            id=attempt_id
        )

        return Response(
            {
                "attempt_id": attempt.id,

                "student_id": (
                    attempt.student.id
                ),

                "student_username": (
                    attempt.student.username
                ),

                "student_email": (
                    attempt.student.email
                ),

                "quiz_id": (
                    attempt.quiz.id
                ),

                "quiz_title": (
                    attempt.quiz.title
                ),

                "score": attempt.score,

                "percentage": (
                    attempt.percentage
                ),

                "correct_answers": (
                    attempt.correct_answers
                ),

                "incorrect_answers": (
                    attempt.incorrect_answers
                ),

                "unanswered": (
                    attempt.unanswered
                ),

                "time_taken": (
                    attempt.time_taken
                ),

                "status": attempt.status,

                "started_at": (
                    attempt.started_at
                ),

                "completed_at": (
                    attempt.completed_at
                ),
            },
            status=status.HTTP_200_OK
        )