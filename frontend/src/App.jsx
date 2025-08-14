import './App.css';
import { Route, Routes, BrowserRouter } from 'react-router-dom';
import Home from './views/home';
import MainWrapper from './layouts/MainWrapper';
import Login from './views/login';
import PrivateRoute from './layouts/PrivateRoute';
import Logout from './views/logout';
import Private from './views/private';
import Register from './views/register';
import Dashboard from './views/dashboard';
import InterviewDashboard from './views/interview';
import InterviewTest from './views/interview-test';
import InterviewMinimal from './views/interview-minimal';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
    return (
        <ErrorBoundary>
            <BrowserRouter
                future={{
                    v7_startTransition: true,
                    v7_relativeSplatPath: true,
                }}
            >
                <MainWrapper>
                    <Routes>
                        <Route
                            path="/private"
                            element={
                                <PrivateRoute>
                                    <Private />
                                </PrivateRoute>
                            }
                        />
                        <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
                        <Route path="/interview" element={<PrivateRoute><ErrorBoundary><InterviewDashboard /></ErrorBoundary></PrivateRoute>} />
                        <Route path="/interview/:campaignId" element={<PrivateRoute><ErrorBoundary><InterviewDashboard /></ErrorBoundary></PrivateRoute>} />
                        <Route path="/" element={<Home />} />
                        <Route path="/login" element={<Login />} />
                        <Route path="/register" element={<Register />} />
                        <Route path="/logout" element={<Logout />} />
                    </Routes>
                </MainWrapper>
            </BrowserRouter>
        </ErrorBoundary>
    );
}

export default App;
