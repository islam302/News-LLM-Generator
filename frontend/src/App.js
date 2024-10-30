import React, { useState, useEffect } from 'react'; // Import useEffect
import axios from 'axios';
import './App.css';

function App() {
    const [title, setTitle] = useState('');
    const [newsType, setNewsType] = useState('');
    const [details, setDetails] = useState('');
    const [response, setResponse] = useState(null);


    useEffect(() => {
        document.title = "News Creator";
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const result = await axios.post('http://127.0.0.1:8000/llm/create/', {
                title,
                newsType,
                details,
            });
            setResponse(result.data);
        } catch (error) {
            console.error("Error:", error);
            setResponse({ error: "حدث خطأ، يرجى المحاولة لاحقًا." });
        }
    };

    return (
        <div className="ai-app-background">
            <div className="overlay"></div>
            <h2>أنشئ الخبر الذي تريده باستخدام الذكاء الاصطناعي</h2>
            <form onSubmit={handleSubmit} className="form">
                <div className="form-group">
                    <label>نوع الخبر</label>
                    <select
                        value={newsType}
                        onChange={(e) => setNewsType(e.target.value)}
                        required
                        className="select-input"
                    >
                        <option value="">اختر نوع الخبر</option>
                        <option value="زيارة">زيارة</option>
                        <option value="حدث">حدث</option>
                        <option value="خبر عاجل">خبر عاجل</option>
                    </select>
                </div>
                <div className="form-group">
                    <label>العنوان</label>
                    <input
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="أدخل عنوان الخبر"
                        required
                    />
                </div>
                <div className="form-group">
                    <label>تفاصيل الخبر</label>
                    <textarea
                        value={details}
                        onChange={(e) => setDetails(e.target.value)}
                        placeholder="أدخل تفاصيل الخبر"
                        rows="5"
                        required
                        className="details-textarea"
                    ></textarea>
                </div>
                <button type="submit" className="submit-btn">إنشاء الخبر</button>
            </form>
            {response && (
                <div className="response-box">
                    {response.error ? (
                        <p className="error">{response.error}</p>
                    ) : (
                        <p className="success">تم إنشاء الخبر بنجاح!</p>
                    )}
                </div>
            )}
        </div>
    );
}

export default App;
