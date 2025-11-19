from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from .models import IssueReport, IssueImage
from .forms import IssueReportForm, IssueImageUploadForm


def create_issue(request):
    if request.method == "POST":
        form = IssueReportForm(request.POST)
        img_form = IssueImageUploadForm(request.POST, request.FILES)
        images = request.FILES.getlist("images")

        if form.is_valid():
            issue = form.save(commit=False)
            issue.created_by = request.user
            issue.save()

            # Save multiple images
            for img in images:
                IssueImage.objects.create(issue=issue, image=img)

            messages.success(request, "Issue submitted successfully.")
            return redirect("issue_detail", issue.id)

    else:
        form = IssueReportForm()
        img_form = IssueImageUploadForm()

    return render(request, "ipqc_issue/create_issue.html", {
        "form": form,
        "img_form": img_form
    })


def issue_detail(request, issue_id):
    issue = get_object_or_404(IssueReport, id=issue_id)
    return render(request, "ipqc_issue/issue_detail.html", {"issue": issue})


def send_reminder(request, issue_id):
    issue = get_object_or_404(IssueReport, id=issue_id)

    # Only creator can send reminder
    if issue.created_by != request.user:
        messages.error(request, "You cannot send reminders for this issue.")
        return redirect("issue_detail", issue_id=issue.id)

    # Check limit
    if issue.reminder_count >= 3:
        messages.warning(request, "Maximum reminders sent (3/3).")
        return redirect("issue_detail", issue_id=issue.id)

    # Update reminder counter
    issue.reminder_count += 1
    issue.last_reminder_at = timezone.now()
    issue.save()

    # TODO: send notification (email / SMS / Lark etc.)

    messages.success(request, f"Reminder sent! ({issue.reminder_count}/3)")
    return redirect("issue_detail", issue_id=issue.id)