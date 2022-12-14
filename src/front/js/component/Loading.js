import React from "react";
import loading from "../../img/loading.gif";

export const Loading = () => {
  return (
    <div className="container-fluid d-flex row-80 loading-bg justify-content-center align-items-center">
      <img src={loading} alt="Cinque Terre" width="300" height="300"></img>
    </div>
  );
};
