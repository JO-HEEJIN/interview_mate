-- Seed data: Interview Questions
-- Category: behavioral, technical, situational
-- Difficulty: easy, medium, hard

-- Behavioral Questions - Easy
INSERT INTO public.questions (category, difficulty, question_text, tags) VALUES
('behavioral', 'easy', 'Tell me about yourself.', ARRAY['introduction', 'self-presentation']),
('behavioral', 'easy', 'Why are you interested in this position?', ARRAY['motivation', 'interest']),
('behavioral', 'easy', 'What are your greatest strengths?', ARRAY['strengths', 'self-awareness']),
('behavioral', 'easy', 'What is your greatest weakness?', ARRAY['weakness', 'self-improvement']),
('behavioral', 'easy', 'Where do you see yourself in 5 years?', ARRAY['goals', 'career-planning']);

-- Behavioral Questions - Medium
INSERT INTO public.questions (category, difficulty, question_text, tags) VALUES
('behavioral', 'medium', 'Tell me about a time you faced a challenging situation at work.', ARRAY['challenge', 'problem-solving', 'STAR']),
('behavioral', 'medium', 'Describe a time when you had to work with a difficult team member.', ARRAY['teamwork', 'conflict', 'STAR']),
('behavioral', 'medium', 'Tell me about a time you failed. How did you handle it?', ARRAY['failure', 'resilience', 'STAR']),
('behavioral', 'medium', 'Describe a situation where you had to meet a tight deadline.', ARRAY['time-management', 'pressure', 'STAR']),
('behavioral', 'medium', 'Tell me about a time you demonstrated leadership.', ARRAY['leadership', 'initiative', 'STAR']);

-- Behavioral Questions - Hard
INSERT INTO public.questions (category, difficulty, question_text, tags) VALUES
('behavioral', 'hard', 'Describe a time when you had to make a difficult decision with incomplete information.', ARRAY['decision-making', 'ambiguity', 'STAR']),
('behavioral', 'hard', 'Tell me about a time you had to convince others to support an unpopular decision.', ARRAY['influence', 'persuasion', 'STAR']),
('behavioral', 'hard', 'Describe a situation where you had to balance multiple competing priorities.', ARRAY['prioritization', 'multi-tasking', 'STAR']),
('behavioral', 'hard', 'Tell me about a time you received critical feedback. How did you respond?', ARRAY['feedback', 'growth', 'STAR']),
('behavioral', 'hard', 'Describe a time when you had to adapt to a significant change at work.', ARRAY['adaptability', 'change-management', 'STAR']);

-- Technical Questions - Easy
INSERT INTO public.questions (category, difficulty, question_text, tags) VALUES
('technical', 'easy', 'What programming languages are you most comfortable with?', ARRAY['programming', 'skills']),
('technical', 'easy', 'How do you stay updated with new technologies?', ARRAY['learning', 'growth']),
('technical', 'easy', 'Describe your experience with version control systems like Git.', ARRAY['git', 'version-control']),
('technical', 'easy', 'What is your development environment setup?', ARRAY['tools', 'workflow']),
('technical', 'easy', 'How do you approach debugging a problem?', ARRAY['debugging', 'problem-solving']);

-- Technical Questions - Medium
INSERT INTO public.questions (category, difficulty, question_text, tags) VALUES
('technical', 'medium', 'Explain the difference between REST and GraphQL APIs.', ARRAY['api', 'architecture']),
('technical', 'medium', 'How would you optimize a slow database query?', ARRAY['database', 'performance']),
('technical', 'medium', 'Describe your experience with CI/CD pipelines.', ARRAY['devops', 'automation']),
('technical', 'medium', 'How do you ensure code quality in your projects?', ARRAY['testing', 'code-review']),
('technical', 'medium', 'Explain how you would design a caching strategy.', ARRAY['caching', 'performance']);

-- Technical Questions - Hard
INSERT INTO public.questions (category, difficulty, question_text, tags) VALUES
('technical', 'hard', 'How would you design a system to handle millions of concurrent users?', ARRAY['scalability', 'system-design']),
('technical', 'hard', 'Explain your approach to microservices architecture.', ARRAY['microservices', 'architecture']),
('technical', 'hard', 'How would you implement authentication and authorization in a distributed system?', ARRAY['security', 'authentication']),
('technical', 'hard', 'Describe how you would handle data consistency in a distributed database.', ARRAY['distributed-systems', 'consistency']),
('technical', 'hard', 'How would you design a real-time notification system?', ARRAY['real-time', 'system-design']);

-- Situational Questions - Easy
INSERT INTO public.questions (category, difficulty, question_text, tags) VALUES
('situational', 'easy', 'What would you do if you disagreed with your manager?', ARRAY['conflict', 'communication']),
('situational', 'easy', 'How would you handle a situation where you made a mistake?', ARRAY['accountability', 'honesty']),
('situational', 'easy', 'What would you do if a teammate was not contributing to a project?', ARRAY['teamwork', 'confrontation']),
('situational', 'easy', 'How would you prioritize tasks if everything seems urgent?', ARRAY['prioritization', 'time-management']),
('situational', 'easy', 'What would you do if you were assigned a task you have never done before?', ARRAY['learning', 'initiative']);

-- Situational Questions - Medium
INSERT INTO public.questions (category, difficulty, question_text, tags) VALUES
('situational', 'medium', 'How would you handle a project that is falling behind schedule?', ARRAY['project-management', 'problem-solving']),
('situational', 'medium', 'What would you do if you discovered a security vulnerability in your code?', ARRAY['security', 'ethics']),
('situational', 'medium', 'How would you approach mentoring a junior developer who is struggling?', ARRAY['mentoring', 'leadership']),
('situational', 'medium', 'What would you do if stakeholders changed requirements mid-project?', ARRAY['flexibility', 'communication']),
('situational', 'medium', 'How would you handle working with legacy code you did not write?', ARRAY['legacy', 'patience']);

-- Situational Questions - Hard
INSERT INTO public.questions (category, difficulty, question_text, tags) VALUES
('situational', 'hard', 'How would you handle a situation where you need to deliver bad news to a client?', ARRAY['communication', 'client-management']),
('situational', 'hard', 'What would you do if you strongly believed the team was making a wrong technical decision?', ARRAY['influence', 'technical-leadership']),
('situational', 'hard', 'How would you approach a situation where two senior team members have conflicting views?', ARRAY['mediation', 'leadership']),
('situational', 'hard', 'What would you do if you were asked to cut corners to meet a deadline?', ARRAY['ethics', 'quality']),
('situational', 'hard', 'How would you handle a situation where you need to take ownership of a failing project?', ARRAY['accountability', 'turnaround']);
