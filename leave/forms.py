from django import forms
from django.utils import timezone
from datetime import datetime
from .models import Leave
from django.contrib.auth.models import User

class LeaveForm(forms.ModelForm):
    current_year = datetime.now().year
    years = [current_year - 2, current_year - 1, current_year]
    year = forms.ChoiceField(
        choices=[(year, year) for year in years],
        label="Year",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Leave
        fields = [
            'leave_type', 'year', 'relief_officer', 'relief_officer_remark',
            'hod_or_line_manager', 'purpose', 'address', 'phone_number',
            'start_date', 'end_date'
        ]
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'relief_officer': forms.Select(attrs={'class': 'form-control'}),
            'hod_or_line_manager': forms.Select(attrs={'class': 'form-control'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'relief_officer_remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Override labels to use full name
        self.fields['relief_officer'].queryset = User.objects.all()
        self.fields['relief_officer'].label_from_instance = lambda obj: obj.get_full_name()

        self.fields['hod_or_line_manager'].queryset = User.objects.all()
        self.fields['hod_or_line_manager'].label_from_instance = lambda obj: obj.get_full_name()

    def clean_start_date(self):
        start_date = self.cleaned_data['start_date']
        if start_date.weekday() in (5, 6):  # Saturday = 5, Sunday = 6
            raise forms.ValidationError("Start date cannot be a weekend.")
        return start_date

    def clean_end_date(self):
        end_date = self.cleaned_data['end_date']
        if end_date.weekday() in (5, 6):
            raise forms.ValidationError("End date cannot be a weekend.")
        return end_date


# class LeaveForm(forms.ModelForm):
#     class Meta:
#         model = Leave
#         fields = ['leave_type', 'year', 'relief_officer', 'hod_or_line_manager', 
#                   'purpose', 'address', 'phone_number', 'start_date', 'end_date']
        
#         widgets = {
#             'leave_type': forms.Select(attrs={'class': 'form-control'}),
#             'year': forms.NumberInput(attrs={'class': 'form-control', 'min': timezone.now().year}),
#             'relief_officer': forms.Select(attrs={'class': 'form-control'}),
#             'hod_or_line_manager': forms.Select(attrs={'class': 'form-control'}),
#             'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
#             'address': forms.TextInput(attrs={'class': 'form-control'}),
#             'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
#             'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#         }

#     def clean_phone_number(self):
#         phone_number = self.cleaned_data.get('phone_number')
#         if not phone_number.isdigit() or len(phone_number) < 10:
#             raise ValidationError("Please enter a valid phone number.")
#         return phone_number

#     def clean(self):
#         cleaned_data = super().clean()
#         start_date = cleaned_data.get('start_date')
#         end_date = cleaned_data.get('end_date')

#         # Ensure the leave end date is not before the start date
#         if start_date and end_date and end_date < start_date:
#             raise ValidationError("End date cannot be before start date.")

#         # Ensure number of days is valid based on leave type
#         leave_type = cleaned_data.get('leave_type')
#         number_of_days = (end_date - start_date).days + 1 if start_date and end_date else 0
#         max_leave_days = {
#             'CL': 5,
#             'AL': 15,
#             'SL': 5,
#             'EL': 14,
#             'ML': 84,
#             'CPL': 10,
#         }

#         if leave_type and number_of_days > max_leave_days.get(leave_type, 0):
#             raise ValidationError(f'{leave_type} can only be up to {max_leave_days.get(leave_type)} days.')

#         return cleaned_data


# from django import forms
# from .models import Leave, LeaveBalance
# from datetime import datetime

# class LeaveApplicationForm(forms.ModelForm):
#     class Meta:
#         model = Leave
#         fields = [
#             'leave_type', 'year', 'relief_officer', 'hod_or_line_manager',
#             'purpose', 'address', 'phone_number', 'start_date', 'end_date'
#         ]
        
#         widgets = {
#             'leave_type': forms.Select(attrs={'class': 'form-select'}),
#             'year': forms.Select(attrs={'class': 'form-select'}),
#             'relief_officer': forms.Select(attrs={'class': 'form-select'}),
#             'hod_or_line_manager': forms.Select(attrs={'class': 'form-select'}),
#             'purpose': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter purpose of leave', 'rows': 3}),
#             'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your contact address', 'rows': 3}),
#             'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
#             'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'readonly': 'readonly'}),
#         }

#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user', None)
#         super().__init__(*args, **kwargs)

#         current_year = datetime.now().year
#         years = [current_year - 2, current_year - 1, current_year]
#         self.fields['year'] = forms.ChoiceField(choices=[(year, year) for year in years], label="Year")

#         # Dynamically generate leave types and their used/remaining days
#         if user:
#             try:
#                 leave_balance = LeaveBalance.objects.get(user=user)

#                 self.fields['leave_type'].choices = [
#                     ('CL', f"Casual Leave (Used: {leave_balance.casual_leave_used} / Remaining: {leave_balance.get_remaining_days('CL')})"),
#                     ('AL', f"Annual Leave (Used: {leave_balance.annual_leave_used} / Remaining: {leave_balance.get_remaining_days('AL')})"),
#                     ('SL', f"Sick Leave (Used: {leave_balance.sick_leave_used} / Remaining: {leave_balance.get_remaining_days('SL')})"),
#                     ('EL', f"Study Leave (Used: {leave_balance.exam_leave_used} / Remaining: {leave_balance.get_remaining_days('EL')})"),
#                     ('ML', f"Maternity Leave (Used: {leave_balance.maternity_leave_used} / Remaining: {leave_balance.get_remaining_days('ML')})"),
#                     ('CPL', f"Compassionate Leave (Used: {leave_balance.compassionate_leave_used} / Remaining: {leave_balance.get_remaining_days('CPL')})"),
#                 ]
#             except LeaveBalance.DoesNotExist:
#                 pass

#     def clean(self):
#         cleaned_data = super().clean()
#         leave_type = cleaned_data.get("leave_type")
#         start_date = cleaned_data.get("start_date")
#         end_date = cleaned_data.get("end_date")
        
#         if leave_type and start_date and end_date:
#             number_of_days = (end_date - start_date).days + 1
#             try:
#                 leave_balance = LeaveBalance.objects.get(user=self.instance.user)
#                 remaining_days = leave_balance.get_remaining_days(leave_type)

#                 if number_of_days > remaining_days:
#                     self.add_error('start_date', f'You cannot request more than {remaining_days} days of {leave_type}.')
#             except LeaveBalance.DoesNotExist:
#                 pass
        
#         return cleaned_data

#     def save(self, commit=True):
#         leave_application = super().save(commit=False)
        
#         if commit:
#             leave_application.save()

#         try:
#             leave_balance = LeaveBalance.objects.get(user=self.instance.user)
#             leave_balance.update_leave_balance(self.cleaned_data['leave_type'], 
#                                                (self.cleaned_data['end_date'] - self.cleaned_data['start_date']).days + 1)
#         except LeaveBalance.DoesNotExist:
#             pass
        
#         return leave_application
