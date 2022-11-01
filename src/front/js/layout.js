import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import ScrollToTop from "./component/scrollToTop";

import { Home } from "./pages/home";
import { Demo } from "./pages/demo";
import { Single } from "./pages/single";
import { Login } from "./pages/login";
import injectContext from "./store/appContext";

import { Navbar } from "./component/navbar";
import { Footer } from "./component/footer";
import { NavbarVertical } from "./component/NavbarVertical";
import { TradingPost } from "./pages/trading-post";

//create your first component
const Layout = () => {
  //the basename is used when your project is published in a subdirectory and not in the root of the domain
  // you can set the basename on the .env file located at the root of this project, E.g: BASENAME=/react-hello-webapp/
  const basename = process.env.BASENAME || "";

  return (
    <div>
      <BrowserRouter basename={basename}>
        <ScrollToTop>
          <Navbar />
          <div className="container-fluid">
            <div className="row view-display">
              <div className="col-1 col-lg-3 p-0">
                <NavbarVertical />
              </div>
              <div className="col-11 col-lg-9">
                <Routes>
                  <Route element={<Home />} path="/" />
                  <Route element={<Login />} path="/login" />
                  <Route element={<TradingPost />} path="/post/trade" />
                  <Route element={<Demo />} path="/demo" />
                  <Route element={<Single />} path="/single/:theid" />
                  <Route element={<h1>Not found!</h1>} />
                </Routes>
              </div>
            </div>
          </div>
          <Footer />
        </ScrollToTop>
      </BrowserRouter>
    </div>
  );
};

export default injectContext(Layout);
