from django.db.models import Avg, Count, Max, Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from quizzes.models import Quiz
from questions.models import Question
from attempts.models import Attempt


class StudentDashboardView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # Get only completed attempts
        attempts = Attempt.objects.filter(
            student=request.user
        ).exclude(
            status="IN_PROGRESS"
        )

        # Total quizzes attempted
        total_attempts = attempts.count()

        # Passed attempts
        passed_attempts = attempts.filter(
            status="PASSED"
        ).count()

        # Failed attempts
        failed_attempts = attempts.filter(
            status="FAILED"
        ).count()

        # Average percentage
        average_score = attempts.aggregate(
            average=Avg("percentage")
        )["average"] or 0

        # Highest percentage
        highest_score = attempts.aggregate(
            highest=Max("percentage")
        )["highest"] or 0

        # Total questions answered
        total_correct = attempts.aggregate(
            total=Count("correct_answers")
        )["total"] or 0

        total_incorrect = attempts.aggregate(
            total=Count("incorrect_answers")
        )["total"] or 0

        total_questions_answered = (
            total_correct + total_incorrect
        )

        # Recent attempts
        recent_attempts = attempts.select_related(
            "quiz"
        ).order_by(
            "-completed_at"
        )[:5]

        recent_data = []

        for attempt in recent_attempts:

            recent_data.append({
                "attempt_id": attempt.id,
                "quiz_id": attempt.quiz.id,
                "quiz_title": attempt.quiz.title,
                "score": attempt.score,
                "percentage": attempt.percentage,
                "status": attempt.status,
                "completed_at": attempt.completed_at,
            })

        return Response(
            {
                "total_quizzes_attempted": total_attempts,
                "total_quizzes_passed": passed_attempts,
                "total_quizzes_failed": failed_attempts,
                "average_score": round(
                    float(average_score),
                    2
                ),
                "highest_score": round(
                    float(highest_score),
                    2
                ),
                "total_questions_answered": (
                    total_questions_answered
                ),
                "recent_attempts": recent_data,
            },
            status=status.HTTP_200_OK
        )


class AdminAnalyticsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # Only admins can access analytics
        if request.user.role != "ADMIN":
            return Response(
                {
                    "error": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # -------------------------
        # USER STATISTICS
        # -------------------------

        total_students = User.objects.filter(
            role="STUDENT"
        ).count()

        active_students = User.objects.filter(
            role="STUDENT",
            is_active=True
        ).count()

        # -------------------------
        # QUIZ STATISTICS
        # -------------------------

        total_quizzes = Quiz.objects.count()

        published_quizzes = Quiz.objects.filter(
            status="Published"
        ).count()

        draft_quizzes = Quiz.objects.filter(
            status="Draft"
        ).count()

        unpublished_quizzes = Quiz.objects.filter(
            status="Unpublished"
        ).count()

        # -------------------------
        # QUESTION STATISTICS
        # -------------------------

        total_questions = Question.objects.count()

        easy_questions = Question.objects.filter(
            difficulty="Easy"
        ).count()

        medium_questions = Question.objects.filter(
            difficulty="Medium"
        ).count()

        hard_questions = Question.objects.filter(
            difficulty="Hard"
        ).count()

        # -------------------------
        # ATTEMPT STATISTICS
        # -------------------------

        completed_attempts = Attempt.objects.filter(
            status__in=[
                "PASSED",
                "FAILED"
            ]
        )

        total_attempts = completed_attempts.count()

        passed_attempts = completed_attempts.filter(
            status="PASSED"
        ).count()

        failed_attempts = completed_attempts.filter(
            status="FAILED"
        ).count()

        # -------------------------
        # SCORE STATISTICS
        # -------------------------

        average_percentage = completed_attempts.aggregate(
            average=Avg("percentage")
        )["average"] or 0

        highest_percentage = completed_attempts.aggregate(
            highest=Max("percentage")
        )["highest"] or 0

        average_score = completed_attempts.aggregate(
            average=Avg("score")
        )["average"] or 0

        # -------------------------
        # POPULAR QUIZZES
        # -------------------------

        popular_quizzes = Quiz.objects.annotate(
            attempt_count=Count(
                "attempts",
                filter=Q(
                    attempts__status__in=[
                        "PASSED",
                        "FAILED"
    ]
)
            )
        ).order_by(
            "-attempt_count"
        )[:5]

        popular_quiz_data = []

        for quiz in popular_quizzes:

            popular_quiz_data.append({
                "quiz_id": quiz.id,
                "quiz_title": quiz.title,
                "attempt_count": quiz.attempt_count,
                "category": quiz.category.name,
            })

        # -------------------------
        # CATEGORY STATISTICS
        # -------------------------

        category_data = []

        from categories.models import Category

        categories = Category.objects.annotate(
            quiz_count=Count("quizzes"),
            attempt_count=Count("quizzes__attempts")
        ).order_by(
            "-attempt_count"
        )

        for category in categories:

            category_data.append({
                "category_id": category.id,
                "category_name": category.name,
                "quiz_count": category.quiz_count,
                "attempt_count": category.attempt_count,
            })

        # -------------------------
        # PASS RATE
        # -------------------------

        if total_attempts > 0:
            pass_rate = (
                passed_attempts / total_attempts
            ) * 100
        else:
            pass_rate = 0

        # -------------------------
        # FINAL RESPONSE
        # -------------------------

        return Response(
            {
                "students": {
                    "total_students": total_students,
                    "active_students": active_students,
                },

                "quizzes": {
                    "total_quizzes": total_quizzes,
                    "published_quizzes": published_quizzes,
                    "draft_quizzes": draft_quizzes,
                    "unpublished_quizzes": unpublished_quizzes,
                },

                "questions": {
                    "total_questions": total_questions,
                    "easy_questions": easy_questions,
                    "medium_questions": medium_questions,
                    "hard_questions": hard_questions,
                },

                "attempts": {
                    "total_attempts": total_attempts,
                    "passed_attempts": passed_attempts,
                    "failed_attempts": failed_attempts,
                    "pass_rate": round(
                        pass_rate,
                        2
                    ),
                },

                "performance": {
                    "average_score": round(
                        float(average_score),
                        2
                    ),
                    "average_percentage": round(
                        float(average_percentage),
                        2
                    ),
                    "highest_percentage": round(
                        float(highest_percentage),
                        2
                    ),
                },

                "popular_quizzes": popular_quiz_data,

                "categories": category_data,
            },
            status=status.HTTP_200_OK
        )
class LeaderboardView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        attempts = Attempt.objects.filter(
            status="PASSED"
        ).select_related(
            "student",
            "quiz"
        )

        leaderboard = []

        students = User.objects.filter(
            role="STUDENT",
            is_active=True
        )

        for student in students:

            student_attempts = attempts.filter(
                student=student
            )

            if not student_attempts.exists():
                continue

            best_attempt = student_attempts.order_by(
                "-percentage",
                "-score"
            ).first()

            average_percentage = student_attempts.aggregate(
                average=Avg("percentage")
            )["average"] or 0

            leaderboard.append({
                "student_id": student.id,
                "username": student.username,
                "best_score": best_attempt.score,
                "best_percentage": best_attempt.percentage,
                "average_percentage": round(
                    float(average_percentage),
                    2
                ),
                "quiz_title": best_attempt.quiz.title,
            })

        # Sort by best percentage first,
        # then best score
        leaderboard.sort(
            key=lambda item: (
                float(item["best_percentage"]),
                float(item["best_score"])
            ),
            reverse=True
        )

        # Add rankings
        for index, student in enumerate(
            leaderboard,
            start=1
        ):
            student["rank"] = index

        return Response(
            leaderboard,
            status=status.HTTP_200_OK
        )