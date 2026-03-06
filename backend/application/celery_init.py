from celery import Celery,Task
from flask import Flask
from celery.schedules import crontab


def celery_init_app(app):
    class FlaskTask(Task):
        def __call__(self,*args:object,**kwargs:object):
            with app.app_context():
                return self.run(*args,**kwargs)
    
    celery_app = Celery(app.name,task_cls=FlaskTask)
    celery_app.config_from_object("celery_config")
    celery_app.set_default()
    app.extensions["celery"]=celery_app #we will get instance of celery app if we write app.celery(in terminal)
    return celery_app
        
    # celery.conf.beat_schedule = {
    #     # Remind students about interviews scheduled for tomorrow (8:00 AM daily)
    #     "daily-interview-reminders": {
    #         "task": "application.task.send_interview_reminders",
    #         "schedule": crontab(hour=8, minute=0),
    #     },
    #     # Remind eligible students about drives whose deadline is tomorrow (9:00 AM daily)
    #     "daily-deadline-reminders": {
    #         "task": "application.task.send_deadline_reminders",
    #         "schedule": crontab(hour=9, minute=0),
    #     },
    #     # Monthly placement report to all approved companies + admin (1st of month, 7:00 AM)
    #     "monthly-placement-report": {
    #         "task": "application.task.send_monthly_report",
    #         "schedule": crontab(hour=7, minute=0, day_of_month=1),
    #     },
    # }

    # class ContextTask(celery.Task):
    #     def __call__(self, *args, **kwargs):
    #         with app.app_context():
    #             return self.run(*args, **kwargs)

    # celery.Task = ContextTask
    # return celery