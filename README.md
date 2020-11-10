# Classroom

## API Endpoints

- [ ] User management
    - [ ] Register
    - [ ] Login
* Registers
    * Submitting Registers
    * Editing Registers
* To-Do
    * ToDo
    * Create ToDo
    * Edit ToDo
* Attendance
    * View Attendance (self)
    * Query Attendance
* Class Pages
    * Create Class Page
    * View Class Page

```
www.school.com/api/v1/register
www.school.com/api/v1/login
www.school.com/api/v1/<classname>/register
www.school.com/api/v1/<classname>/register/<timestamp>
```

www.school.com/api/v1/<classname>/register <- this is the api endpoint
www.school.com/<classname>/register <- this is where the user ends up to view the data at the api endpoint

APIs in flask - endpoints in Vue