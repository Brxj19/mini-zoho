import { useNavigate } from "react-router-dom";

import { Icon } from "./Icon";

export function BackButton({ fallbackTo = "/", label = "Back" }) {
  const navigate = useNavigate();

  function handleBack() {
    if (window.history.length > 1) {
      navigate(-1);
      return;
    }
    navigate(fallbackTo);
  }

  return (
    <button className="ghost-button back-button" type="button" onClick={handleBack}>
      <Icon name="arrowLeft" size={16} />
      <span>{label}</span>
    </button>
  );
}
