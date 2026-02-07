--
-- PostgreSQL database dump
--

\restrict FJqGqkxhPXPhn2kldK19jqrKejQObQxWrRD71bdcRsEE9daAONIl7UF4YR3QXmA

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
-- Name: authprovider; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.authprovider AS ENUM (
    'EMAIL'
);


--
-- Name: chatstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.chatstatus AS ENUM (
    'ACTIVE',
    'COMPLETED',
    'FINALIZED'
);


--
-- Name: goalcategory; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.goalcategory AS ENUM (
    'HEALTH',
    'CAREER',
    'EDUCATION',
    'FINANCE',
    'PERSONAL',
    'OTHER'
);


--
-- Name: goalstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.goalstatus AS ENUM (
    'ACTIVE',
    'COMPLETED',
    'PAUSED',
    'ABANDONED'
);


--
-- Name: goaltype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.goaltype AS ENUM (
    'SHORT_TERM',
    'LONG_TERM',
    'RESOLUTION'
);


--
-- Name: habitstrength; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.habitstrength AS ENUM (
    'FORMING',
    'DEVELOPING',
    'ESTABLISHED',
    'AUTOMATIC'
);


--
-- Name: insighttype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.insighttype AS ENUM (
    'PATTERN',
    'STRENGTH',
    'WEAKNESS',
    'RECOMMENDATION',
    'WARNING'
);


--
-- Name: learningstyle; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.learningstyle AS ENUM (
    'VISUAL',
    'AUDITORY',
    'READING',
    'KINESTHETIC'
);


--
-- Name: messagerole; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.messagerole AS ENUM (
    'USER',
    'ASSISTANT',
    'SYSTEM'
);


--
-- Name: motivationtype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.motivationtype AS ENUM (
    'INTRINSIC',
    'EXTRINSIC',
    'ACHIEVEMENT',
    'AFFILIATION',
    'POWER'
);


--
-- Name: personalitytype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.personalitytype AS ENUM (
    'DRIVER',
    'ANALYTICAL',
    'EXPRESSIVE',
    'AMIABLE'
);


--
-- Name: taskfrequency; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.taskfrequency AS ENUM (
    'DAILY',
    'WEEKLY',
    'MONTHLY',
    'ONE_TIME'
);


--
-- Name: taskpriority; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.taskpriority AS ENUM (
    'LOW',
    'MEDIUM',
    'HIGH'
);


--
-- Name: taskstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.taskstatus AS ENUM (
    'PENDING',
    'IN_PROGRESS',
    'COMPLETED',
    'SKIPPED'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: chat_messages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chat_messages (
    id integer NOT NULL,
    session_id integer NOT NULL,
    role public.messagerole NOT NULL,
    content character varying NOT NULL,
    created_at timestamp without time zone NOT NULL
);


--
-- Name: chat_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.chat_messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: chat_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.chat_messages_id_seq OWNED BY public.chat_messages.id;


--
-- Name: chat_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chat_sessions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    title character varying,
    status public.chatstatus NOT NULL,
    goal_id integer,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: chat_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.chat_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: chat_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.chat_sessions_id_seq OWNED BY public.chat_sessions.id;


--
-- Name: daily_progress; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.daily_progress (
    id integer NOT NULL,
    user_id integer NOT NULL,
    goal_id integer,
    date timestamp without time zone NOT NULL,
    tasks_planned integer NOT NULL,
    tasks_completed integer NOT NULL,
    tasks_skipped integer NOT NULL,
    completion_rate double precision NOT NULL,
    total_minutes_logged integer NOT NULL,
    mood_score integer,
    energy_level integer,
    notes character varying,
    created_at timestamp without time zone NOT NULL
);


--
-- Name: daily_progress_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.daily_progress_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: daily_progress_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.daily_progress_id_seq OWNED BY public.daily_progress.id;


--
-- Name: goals; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.goals (
    id integer NOT NULL,
    user_id integer NOT NULL,
    chat_session_id integer,
    title character varying NOT NULL,
    description character varying,
    category public.goalcategory NOT NULL,
    goal_type public.goaltype NOT NULL,
    target_date date,
    status public.goalstatus NOT NULL,
    progress integer NOT NULL,
    motivation_score integer,
    feasibility_score integer,
    clarity_score integer,
    smart_specific character varying,
    smart_measurable character varying,
    smart_achievable character varying,
    smart_relevant character varying,
    smart_time_bound character varying,
    sustainability_score integer,
    burnout_risk character varying,
    identified_obstacles json,
    success_criteria json,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: goals_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.goals_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: goals_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.goals_id_seq OWNED BY public.goals.id;


--
-- Name: habit_loops; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.habit_loops (
    id integer NOT NULL,
    user_id integer NOT NULL,
    task_id integer,
    goal_id integer,
    name character varying NOT NULL,
    description character varying,
    cue character varying NOT NULL,
    routine character varying NOT NULL,
    reward character varying NOT NULL,
    strength public.habitstrength NOT NULL,
    days_tracked integer NOT NULL,
    current_streak integer NOT NULL,
    best_streak integer NOT NULL,
    completion_rate double precision NOT NULL,
    target_time character varying,
    target_days character varying,
    is_active boolean NOT NULL,
    last_performed_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: habit_loops_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.habit_loops_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: habit_loops_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.habit_loops_id_seq OWNED BY public.habit_loops.id;


--
-- Name: milestones; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.milestones (
    id integer NOT NULL,
    goal_id integer NOT NULL,
    title character varying NOT NULL,
    description character varying,
    target_date date,
    "order" integer NOT NULL,
    is_completed boolean NOT NULL,
    completed_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL
);


--
-- Name: milestones_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.milestones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: milestones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.milestones_id_seq OWNED BY public.milestones.id;


--
-- Name: system_prompts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.system_prompts (
    id integer NOT NULL,
    key character varying NOT NULL,
    description character varying NOT NULL,
    content character varying NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: system_prompts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.system_prompts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: system_prompts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.system_prompts_id_seq OWNED BY public.system_prompts.id;


--
-- Name: tasks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tasks (
    id integer NOT NULL,
    milestone_id integer,
    goal_id integer NOT NULL,
    title character varying NOT NULL,
    description character varying,
    due_date date,
    status public.taskstatus NOT NULL,
    priority public.taskpriority NOT NULL,
    frequency public.taskfrequency NOT NULL,
    estimated_minutes integer NOT NULL,
    streak_count integer NOT NULL,
    best_streak integer NOT NULL,
    last_completed_at timestamp without time zone,
    times_completed integer NOT NULL,
    times_skipped integer NOT NULL,
    habit_cue character varying,
    habit_reward character varying,
    completed_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL
);


--
-- Name: tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tasks_id_seq OWNED BY public.tasks.id;


--
-- Name: user_insights; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_insights (
    id integer NOT NULL,
    user_id integer NOT NULL,
    goal_id integer,
    insight_type public.insighttype NOT NULL,
    title character varying NOT NULL,
    description character varying NOT NULL,
    source_agent character varying NOT NULL,
    importance character varying NOT NULL,
    confidence double precision NOT NULL,
    is_actionable boolean NOT NULL,
    action_taken boolean NOT NULL,
    data json,
    created_at timestamp without time zone NOT NULL,
    expires_at timestamp without time zone
);


--
-- Name: user_insights_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_insights_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_insights_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_insights_id_seq OWNED BY public.user_insights.id;


--
-- Name: user_profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_profiles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    learning_style public.learningstyle,
    motivation_type public.motivationtype,
    personality_type public.personalitytype,
    best_time_of_day character varying,
    best_days character varying,
    avg_focus_duration integer,
    preferred_goal_type character varying,
    preferred_task_size character varying,
    total_goals_completed integer NOT NULL,
    total_tasks_completed integer NOT NULL,
    avg_completion_rate double precision NOT NULL,
    longest_streak integer NOT NULL,
    current_stress_level integer NOT NULL,
    current_motivation_level integer NOT NULL,
    current_confidence_level integer NOT NULL,
    preferred_reminder_frequency character varying,
    preferred_communication_style character varying,
    strengths json,
    challenges json,
    "values" json,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: user_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_profiles_id_seq OWNED BY public.user_profiles.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying NOT NULL,
    password_hash character varying,
    name character varying NOT NULL,
    avatar_url character varying,
    auth_provider public.authprovider NOT NULL,
    is_active boolean NOT NULL,
    is_superuser boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    token_limit integer NOT NULL,
    tokens_used integer NOT NULL,
    quota_reset_at timestamp without time zone
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: chat_messages id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_messages ALTER COLUMN id SET DEFAULT nextval('public.chat_messages_id_seq'::regclass);


--
-- Name: chat_sessions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_sessions ALTER COLUMN id SET DEFAULT nextval('public.chat_sessions_id_seq'::regclass);


--
-- Name: daily_progress id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.daily_progress ALTER COLUMN id SET DEFAULT nextval('public.daily_progress_id_seq'::regclass);


--
-- Name: goals id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.goals ALTER COLUMN id SET DEFAULT nextval('public.goals_id_seq'::regclass);


--
-- Name: habit_loops id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.habit_loops ALTER COLUMN id SET DEFAULT nextval('public.habit_loops_id_seq'::regclass);


--
-- Name: milestones id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.milestones ALTER COLUMN id SET DEFAULT nextval('public.milestones_id_seq'::regclass);


--
-- Name: system_prompts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_prompts ALTER COLUMN id SET DEFAULT nextval('public.system_prompts_id_seq'::regclass);


--
-- Name: tasks id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks ALTER COLUMN id SET DEFAULT nextval('public.tasks_id_seq'::regclass);


--
-- Name: user_insights id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_insights ALTER COLUMN id SET DEFAULT nextval('public.user_insights_id_seq'::regclass);


--
-- Name: user_profiles id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_profiles ALTER COLUMN id SET DEFAULT nextval('public.user_profiles_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: chat_messages chat_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_pkey PRIMARY KEY (id);


--
-- Name: chat_sessions chat_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_sessions
    ADD CONSTRAINT chat_sessions_pkey PRIMARY KEY (id);


--
-- Name: daily_progress daily_progress_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.daily_progress
    ADD CONSTRAINT daily_progress_pkey PRIMARY KEY (id);


--
-- Name: goals goals_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.goals
    ADD CONSTRAINT goals_pkey PRIMARY KEY (id);


--
-- Name: habit_loops habit_loops_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.habit_loops
    ADD CONSTRAINT habit_loops_pkey PRIMARY KEY (id);


--
-- Name: milestones milestones_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.milestones
    ADD CONSTRAINT milestones_pkey PRIMARY KEY (id);


--
-- Name: system_prompts system_prompts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_prompts
    ADD CONSTRAINT system_prompts_pkey PRIMARY KEY (id);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: user_insights user_insights_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_insights
    ADD CONSTRAINT user_insights_pkey PRIMARY KEY (id);


--
-- Name: user_profiles user_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_chat_messages_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_chat_messages_session_id ON public.chat_messages USING btree (session_id);


--
-- Name: ix_chat_sessions_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_chat_sessions_user_id ON public.chat_sessions USING btree (user_id);


--
-- Name: ix_daily_progress_goal_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_daily_progress_goal_id ON public.daily_progress USING btree (goal_id);


--
-- Name: ix_daily_progress_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_daily_progress_user_id ON public.daily_progress USING btree (user_id);


--
-- Name: ix_goals_chat_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_goals_chat_session_id ON public.goals USING btree (chat_session_id);


--
-- Name: ix_goals_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_goals_user_id ON public.goals USING btree (user_id);


--
-- Name: ix_habit_loops_goal_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_habit_loops_goal_id ON public.habit_loops USING btree (goal_id);


--
-- Name: ix_habit_loops_task_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_habit_loops_task_id ON public.habit_loops USING btree (task_id);


--
-- Name: ix_habit_loops_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_habit_loops_user_id ON public.habit_loops USING btree (user_id);


--
-- Name: ix_milestones_goal_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_milestones_goal_id ON public.milestones USING btree (goal_id);


--
-- Name: ix_system_prompts_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_system_prompts_key ON public.system_prompts USING btree (key);


--
-- Name: ix_tasks_goal_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_tasks_goal_id ON public.tasks USING btree (goal_id);


--
-- Name: ix_tasks_milestone_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_tasks_milestone_id ON public.tasks USING btree (milestone_id);


--
-- Name: ix_user_insights_goal_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_insights_goal_id ON public.user_insights USING btree (goal_id);


--
-- Name: ix_user_insights_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_insights_user_id ON public.user_insights USING btree (user_id);


--
-- Name: ix_user_profiles_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_user_profiles_user_id ON public.user_profiles USING btree (user_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: chat_messages chat_messages_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.chat_sessions(id);


--
-- Name: chat_sessions chat_sessions_goal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_sessions
    ADD CONSTRAINT chat_sessions_goal_id_fkey FOREIGN KEY (goal_id) REFERENCES public.goals(id);


--
-- Name: chat_sessions chat_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_sessions
    ADD CONSTRAINT chat_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: daily_progress daily_progress_goal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.daily_progress
    ADD CONSTRAINT daily_progress_goal_id_fkey FOREIGN KEY (goal_id) REFERENCES public.goals(id);


--
-- Name: daily_progress daily_progress_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.daily_progress
    ADD CONSTRAINT daily_progress_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: goals goals_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.goals
    ADD CONSTRAINT goals_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: habit_loops habit_loops_goal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.habit_loops
    ADD CONSTRAINT habit_loops_goal_id_fkey FOREIGN KEY (goal_id) REFERENCES public.goals(id);


--
-- Name: habit_loops habit_loops_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.habit_loops
    ADD CONSTRAINT habit_loops_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id);


--
-- Name: habit_loops habit_loops_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.habit_loops
    ADD CONSTRAINT habit_loops_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: milestones milestones_goal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.milestones
    ADD CONSTRAINT milestones_goal_id_fkey FOREIGN KEY (goal_id) REFERENCES public.goals(id);


--
-- Name: tasks tasks_goal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_goal_id_fkey FOREIGN KEY (goal_id) REFERENCES public.goals(id);


--
-- Name: tasks tasks_milestone_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_milestone_id_fkey FOREIGN KEY (milestone_id) REFERENCES public.milestones(id);


--
-- Name: user_insights user_insights_goal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_insights
    ADD CONSTRAINT user_insights_goal_id_fkey FOREIGN KEY (goal_id) REFERENCES public.goals(id);


--
-- Name: user_insights user_insights_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_insights
    ADD CONSTRAINT user_insights_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_profiles user_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict FJqGqkxhPXPhn2kldK19jqrKejQObQxWrRD71bdcRsEE9daAONIl7UF4YR3QXmA

