from django import template

register = template.Library()

@register.filter
def get_marks_data(marks_data, keys):
    print(f"Type of keys: {type(keys)}")
    print(f"Value of keys: {keys}")

    if not keys or not isinstance(keys, str):
        return None

    try:
        student_id, subject_id = map(int, keys.split(','))
    except (ValueError, TypeError):
        return None

    student_marks = marks_data.get(student_id, {})
    return student_marks.get(subject_id, {'marks_obtained': '', 'out_of': ''})