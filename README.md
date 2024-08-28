
# Personal Study System

This is a personal project that I created to help track and analyze my schoolwork performance. It's designed to where you can add assessments and subjects and their details, remove them, and edit their aspects. There are also visual graphs and representations of grades' percentages and classifications.

I also made this project to test and showcase all the skills I've learned throughout my journey as a programer. Hopefuly this is one of the many projects I will code (help code) in my career.


## Features
- Managing assessments
The assessments page is equipped with the tools needed to view, add, remove, analyze and search for an exam or a quiz in the sidebar. The main table shows all the exams and quizzes for a specific request, if the user searches by date or information then all the quizzes and exams by those specifications will appear. If the user selects a subject then all the exams and quizzes per that subject will appear.
- Managing subjects
The subjects page has a set of default subjects: English, Math, Biology, Chemistry and Physics. The subjects page offers a sidebar where the users can view, add, and remove, subjects easily and add and edit specific
topics for each subject. The accordion-style part of the page is divided into 3 sections: Topics, Recent Assessments 
and Weaknesses. The topics section shows all the topics for a selected subject, the recent assessments section shows the last 5 quizzes and exams for a selected subject, and the weaknesses section shows the topics where the user is moderately strong or weak  (calculated through the weakness grading function based on the difficulty and strength listed).
- Writing and editing documents
On the documents page, the user can either make a new document, edit a previous one or remove one. All the valid documents appear in the options. Once the user has made a new document or chosen one they can write in the text box, alter or add to their text and save their changes. *Note:* If the user does not save the file then all changes will be deleted upon reloading the page.
- Built-in AI chatbot functionality
On the AI assistant page, a built-in AI chatbot is avaliable based on the Gemini API by google. If the user passes a query that contains RECORD a recording of the users next 5 seconds will be used as a query. If the user passes RECORD followed by a number thats the ammount of seconds that will be recorded afterwards. If the user pasess RESET only, then the AI's context and history will be reset. If the user passes EXIT only, then the AI's context will be reset and the user will be redirected to the home page.
### Coding Languages Used

I used Python, Flask, Javascript, JQuery and Django for the dynamic aspect of the website, HTML and CSS for the static and design aspects. I used Chart.js library for the graphs and charts, and the Bootstrap css library for CSS and HTML classes and pre-coded elements. As well as multiple libraries listed in the requirements.txt file and APIs listed in the acknowledgements

## Acknowledgements

 - [Unsplash API for photos](https://unsplash.com/developers)
 - [API Ninjas  for fun facts](https://api-ninjas.com/)
 - [Gemini API for AI generated text](https://www.google.com/aclk?sa=l&ai=DChcSEwjo3O3i5peIAxXZoGgJHWRlDeUYABAAGgJ3Zg&co=1&ase=2&gclid=CjwKCAjwlbu2BhA3EiwA3yXyu76gLoVFwFmTJ28xVcO8sRNHP8QJHNFCMiurFijAvSiEEpf-1FEHzxoC92IQAvD_BwE&sig=AOD64_1TgPz7XziCe2TxCIe7K-J_WhocBA&q&nis=4&adurl&ved=2ahUKEwiq1uji5peIAxWGUaQEHaY8AS8Q0Qx6BAgJEAE)
 - [AssemblyAI for STT queries](https://www.assemblyai.com/dashboard/signup)
 - [Bootstrap for CSS and HTML elements](https://getbootstrap.com/docs/5.0/getting-started/introduction/)
 - [Color Hunt for all colors and insparation](https://colorhunt.co/)
 - [CS50X Foundational programming](https://cs50.harvard.edu/x/2024/)
 - [CS50P for Python focused programming](https://cs50.harvard.edu/python)


## Authors

- [@NaderEdward](https://github.com/NaderEdward)