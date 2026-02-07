--
-- PostgreSQL database dump
--

\restrict NNkf8Q4xwbGQlMZ4J8Lie7UxtiLpNdbRJu1vSDUTFjLv9mtBD2RcneG8cx1YR4Y

-- Dumped from database version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: milesync_user
--

INSERT INTO public.users VALUES (1, 'admin@milesync.demo', '$2b$12$Qp.SKsaJk2Y7aDBaHlLihOnuGguI0UEGtfbdH45y3/JklLf82oL06', 'Admin', NULL, 'EMAIL', true, true, '2026-02-07 09:09:43.120193', '2026-02-07 09:09:43.120207', 2000, 0, NULL);
INSERT INTO public.users VALUES (2, 'user@milesync.demo', '$2b$12$2SKC7DKDkEO3WV0Cbql2ruBdbZaaqg63dQg/U/PadKknET2kc/avO', 'Super User', NULL, 'EMAIL', true, false, '2026-02-07 09:09:43.389541', '2026-02-07 09:09:43.389553', 2000, 0, NULL);


--
-- Data for Name: goals; Type: TABLE DATA; Schema: public; Owner: milesync_user
--



--
-- Data for Name: chat_sessions; Type: TABLE DATA; Schema: public; Owner: milesync_user
--



--
-- Data for Name: chat_messages; Type: TABLE DATA; Schema: public; Owner: milesync_user
--



--
-- Data for Name: daily_progress; Type: TABLE DATA; Schema: public; Owner: milesync_user
--



--
-- Data for Name: milestones; Type: TABLE DATA; Schema: public; Owner: milesync_user
--



--
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: milesync_user
--



--
-- Data for Name: habit_loops; Type: TABLE DATA; Schema: public; Owner: milesync_user
--



--
-- Data for Name: system_prompts; Type: TABLE DATA; Schema: public; Owner: milesync_user
--



--
-- Data for Name: user_insights; Type: TABLE DATA; Schema: public; Owner: milesync_user
--



--
-- Data for Name: user_profiles; Type: TABLE DATA; Schema: public; Owner: milesync_user
--



--
-- Name: chat_messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: milesync_user
--

SELECT pg_catalog.setval('public.chat_messages_id_seq', 1, false);


--
-- Name: chat_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: milesync_user
--

SELECT pg_catalog.setval('public.chat_sessions_id_seq', 1, false);


--
-- Name: daily_progress_id_seq; Type: SEQUENCE SET; Schema: public; Owner: milesync_user
--

SELECT pg_catalog.setval('public.daily_progress_id_seq', 1, false);


--
-- Name: goals_id_seq; Type: SEQUENCE SET; Schema: public; Owner: milesync_user
--

SELECT pg_catalog.setval('public.goals_id_seq', 1, false);


--
-- Name: habit_loops_id_seq; Type: SEQUENCE SET; Schema: public; Owner: milesync_user
--

SELECT pg_catalog.setval('public.habit_loops_id_seq', 1, false);


--
-- Name: milestones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: milesync_user
--

SELECT pg_catalog.setval('public.milestones_id_seq', 1, false);


--
-- Name: system_prompts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: milesync_user
--

SELECT pg_catalog.setval('public.system_prompts_id_seq', 1, false);


--
-- Name: tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: milesync_user
--

SELECT pg_catalog.setval('public.tasks_id_seq', 1, false);


--
-- Name: user_insights_id_seq; Type: SEQUENCE SET; Schema: public; Owner: milesync_user
--

SELECT pg_catalog.setval('public.user_insights_id_seq', 1, false);


--
-- Name: user_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: milesync_user
--

SELECT pg_catalog.setval('public.user_profiles_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: milesync_user
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- PostgreSQL database dump complete
--

\unrestrict NNkf8Q4xwbGQlMZ4J8Lie7UxtiLpNdbRJu1vSDUTFjLv9mtBD2RcneG8cx1YR4Y

