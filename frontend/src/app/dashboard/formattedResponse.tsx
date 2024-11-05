import React from "react";

interface FormattedResponseProps {
  answer: string;
}

const FormattedResponse: React.FC<FormattedResponseProps> = ({ answer }) => {
  const processAnswer = (text: string) => {
    if (!text || typeof text !== "string") {
      return <div>No content available</div>;
    }

    try {
      // Split by company sections
      const sections = text.split(/(?=\*\*[A-Z][^:]+:)/);

      return sections.map((section, index) => {
        if (!section.trim()) return null;

        // Extract company name if present
        const companyMatch = section.match(/\*\*([^:]+):/);
        const companyName = companyMatch ? companyMatch[1] : "";

        // Split content into subsections
        const contentWithoutCompany = section.replace(
          companyMatch?.[0] || "",
          ""
        );
        const subsections = contentWithoutCompany
          .split(/(?=-\s*\*\*[^:]+:\*\*)/g)
          .filter(Boolean);

        return (
          <div key={index}>
            {companyName && (
              <div className="font-bold text-lg mb-2">{companyName.trim()}</div>
            )}
            {subsections.map((subsection, subIndex) => {
              // Extract subsection title if present
              const titleMatch = subsection.match(/-\s*\*\*([^:]+):\*\*/);
              const title = titleMatch ? titleMatch[1] : "";
              const content = subsection
                .replace(titleMatch?.[0] || "", "")
                .split("-")
                .filter((item) => item && item.trim())
                .map((item) => item.trim());

              return (
                <div key={subIndex} className="mb-3">
                  {title && (
                    <div className="font-semibold mb-1">{title.trim()}</div>
                  )}
                  <ul className="list-disc pl-6 space-y-1">
                    {content.map((item, itemIndex) => (
                      <li key={itemIndex}>
                        {item.replace(/\*\*/g, "").trim()}
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>
        );
      });
    } catch (error) {
      return (
        <div className="whitespace-pre-wrap">{text.replace(/\*\*/g, "")}</div>
      );
    }
  };

  return <div className="text-base">{processAnswer(answer)}</div>;
};

export default FormattedResponse;
