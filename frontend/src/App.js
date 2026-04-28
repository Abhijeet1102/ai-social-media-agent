import { useState, useEffect } from "react";
import "./App.css";

const BASE_URL = process.env.REACT_APP_API_URL ? .replace(/\/$/, "");


function App() {
    const [topic, setTopic] = useState("");
    const [result, setResult] = useState("");
    const [showModal, setShowModal] = useState(false);

    const [date, setDate] = useState("");
    const [time, setTime] = useState("");

    // AUTH
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [isSignup, setIsSignup] = useState(false);

    // DATA
    const [posts, setPosts] = useState([]);
    const [scheduledData, setScheduledData] = useState([]);

    // AUTO LOGIN
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (token) setIsLoggedIn(true);
    }, []);

    useEffect(() => {
        if (isLoggedIn) {
            fetchPosts();
            fetchScheduled();
        }
    }, [isLoggedIn]);

    // FETCH POSTS
    const fetchPosts = async() => {
        const token = localStorage.getItem("token");

        const res = await fetch(`${BASE_URL}/posts`, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });

        const data = await res.json();
        setPosts(data);
    };

    // FETCH SCHEDULED
    const fetchScheduled = async() => {
        const token = localStorage.getItem("token");

        const res = await fetch(`${BASE_URL}/scheduled`, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });

        const data = await res.json();
        setScheduledData(data);
    };

    // LOGIN
    const handleLogin = async() => {
        const res = await fetch(`${BASE_URL}/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: `username=${username}&password=${password}`,
        });

        const data = await res.json();

        if (data.access_token) {
            localStorage.setItem("token", data.access_token);
            setIsLoggedIn(true);
            alert("Login Successful 🚀");
        } else {
            alert(data.detail || "Login Failed");
        }
    };

    // SIGNUP
    const handleSignup = async() => {
        const res = await fetch(`${BASE_URL}/signup`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: `username=${username}&password=${password}`,
        });

        const data = await res.json();

        alert(data.msg || data.detail);

        if (data.msg) setIsSignup(false);
    };

    // LOGOUT
    const handleLogout = () => {
        localStorage.removeItem("token");
        setIsLoggedIn(false);
        setPosts([]);
        setScheduledData([]);
        setResult("");
    };

    // GENERATE
    const generateContent = async() => {
        const token = localStorage.getItem("token");

        const res = await fetch(
            `${BASE_URL}/generate?topic=${topic}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            }
        );

        const data = await res.json();
        setResult(data.result);

        fetchPosts();
    };

    // SCHEDULE
    const schedulePost = async() => {
        const token = localStorage.getItem("token");

        if (!result || !date || !time) {
            alert("Fill all fields!");
            return;
        }

        const res = await fetch(`${BASE_URL}/schedule`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
                content: result,
                date,
                time,
            }),
        });

        const data = await res.json();
        alert(data.msg);

        setDate("");
        setTime("");

        fetchScheduled();
    };


    return ( <
        div className = "app" >

        { /* HERO */ } <
        header className = "hero" >
        <
        h1 > AI Social Media Automation < /h1> <
        p > Create, Schedule & Grow with AI < /p>

        <
        button onClick = {
            () => setShowModal(true)
        } >
        Connect Accounts <
        /button>

        {
            isLoggedIn && ( <
                button onClick = { handleLogout }
                style = {
                    { marginLeft: "10px" }
                } >
                Logout <
                /button>
            )
        } <
        /header>

        { /* LOGIN / SIGNUP */ } {
            !isLoggedIn && ( <
                div style = {
                    { textAlign: "center", marginTop: "20px" }
                } >
                <
                h3 > { isSignup ? "Signup" : "Login" } < /h3>

                <
                input placeholder = "Username"
                value = { username }
                onChange = {
                    (e) => setUsername(e.target.value)
                }
                />

                <
                br / > < br / >

                <
                input type = "password"
                placeholder = "Password"
                value = { password }
                onChange = {
                    (e) => setPassword(e.target.value)
                }
                />

                <
                br / > < br / >

                {
                    isSignup ? ( <
                        button onClick = { handleSignup } > Signup < /button>
                    ) : ( <
                        button onClick = { handleLogin } > Login < /button>
                    )
                }

                <
                p style = {
                    { cursor: "pointer", color: "blue", marginTop: "10px" }
                }
                onClick = {
                    () => setIsSignup(!isSignup)
                } > {
                    isSignup ?
                    "Already have account? Login" : "New user? Signup"
                } <
                /p> < /
                div >
            )
        }

        { /* GENERATE */ } {
            isLoggedIn && ( <
                section className = "generator" >
                <
                h2 > Generate Content < /h2>

                <
                input type = "text"
                placeholder = "Enter topic..."
                value = { topic }
                onChange = {
                    (e) => setTopic(e.target.value)
                }
                />

                <
                button onClick = { generateContent } > Generate < /button>

                {
                    result && ( <
                        div className = "result-card" >
                        <
                        h3 > Generated Content < /h3> <
                        p > { result } < /p>

                        <
                        h4 > Schedule Post < /h4>

                        <
                        input type = "date"
                        value = { date }
                        onChange = {
                            (e) => setDate(e.target.value)
                        }
                        />

                        <
                        input type = "time"
                        value = { time }
                        onChange = {
                            (e) => setTime(e.target.value)
                        }
                        />

                        <
                        button onClick = { schedulePost } > Schedule < /button> < /
                        div >
                    )
                } <
                /section>
            )
        }

        { /* DASHBOARD */ } {
            isLoggedIn && ( <
                section >
                <
                h2 > Dashboard < /h2>

                {
                    posts.map((post, index) => ( <
                        div key = { index }
                        className = "result-card" >
                        <
                        p > { post.result } < /p> <
                        small > Topic: { post.topic } < /small> < /
                        div >
                    ))
                } <
                /section>
            )
        }

        { /* SCHEDULED POSTS */ } {
            isLoggedIn && ( <
                section >
                <
                h2 > ⏳Scheduled Posts < /h2>

                {
                    scheduledData.map((post, index) => ( <
                        div key = { index }
                        className = "result-card" >
                        <
                        p > { post.content } < /p> <
                        small > 📅{ post.date }⏰ { post.time } | Status: { post.status } <
                        /small> < /
                        div >
                    ))
                } <
                /section>
            )
        }

        { /* MODAL */ } {
            showModal && ( <
                div className = "modal" >
                <
                div className = "modal-content" >
                <
                h2 > Connect Your Accounts < /h2>

                <
                div className = "icons" >
                <
                button > 📸Instagram < /button> <
                button > 💼LinkedIn < /button> <
                button > ▶️YouTube < /button> <
                button > 📘Facebook < /button> < /
                div >

                <
                button onClick = {
                    () => setShowModal(false)
                } > Close < /button> < /
                div > <
                /div>
            )
        }

        <
        /div>
    );
}

export default App;
export default App;