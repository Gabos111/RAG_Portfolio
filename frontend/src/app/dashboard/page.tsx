"use client";
import React from "react";
import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import {
  CarouselItem,
  CarouselContent,
  CarouselNext,
  CarouselPrevious,
  Carousel,
} from "@/components/ui/carousel";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useEffect } from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  LabelList,
} from "recharts";
import axios from "axios";
import { useCallback } from "react";
import debounce from "lodash/debounce";

interface portfolioData {
  name: string;
  ticker: string;
  percentage: number;
  color: string;
  sector: string;
}

interface PriceData {
  Date: string;
  variable: string;
  value: number;
}

interface NormalizedPriceData {
  Date: string;
  [key: string]: number | string;
}

interface RiskReturnData {
  stock: string;
  annualReturn: number;
  annualVolatility: number;
}

interface Message {
  role: "user" | "bot";
  content: string;
}

interface MetricsData {
  basic_metrics: {
    "Total Return": number;
    "Annual Return": number;
    "Annual Volatility": number;
    "Sharpe Ratio": number;
    "Max Drawdown": number;
  };
  risk_metrics: {
    Beta: number;
    Alpha: number;
    "Information Ratio": number;
  };
}

export default function Dashboard() {
  const [portfolioData, setPortfolioData] = useState<portfolioData[]>([]);
  const [inputValue, setInputValue] = useState("");
  // Chart data states
  const [pricesData, setPricesData] = useState<PriceData[]>([]);
  const [stockPrices, setStockPrices] = useState<{
    [key: string]: Array<{ date: string; price: number }>;
  }>({});
  const [normalizedPrices, setNormalizedPrices] = useState<
    NormalizedPriceData[]
  >([]);
  const [riskReturnData, setRiskReturnData] = useState<RiskReturnData[]>([]);
  const [metricsData, setMetricsData] = useState<MetricsData | null>(null);
  const [messages, setMessages] = useState<Message[]>([
    { role: "bot", content: "Hello! How can I assist you today?" },
  ]);

  useEffect(() => {
    // Fetch portfolio data from the backend API
    const fetchPortfolioData = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/portfolio");
        setPortfolioData(response.data);

        //metrics
        const metricsResponse = await axios.get(
          "http://127.0.0.1:8000/portfolio/metrics"
        );
        setMetricsData(metricsResponse.data);

        // Fetch prices for small charts
        const pricesResponse = await axios.get<PriceData[]>(
          "http://127.0.0.1:8000/portfolio/prices"
        );
        setPricesData(pricesResponse.data);

        // Process data for small charts
        const stockPricesData: {
          [key: string]: Array<{ date: string; price: number }>;
        } = {};
        pricesResponse.data.forEach((item) => {
          if (!stockPricesData[item.variable]) {
            stockPricesData[item.variable] = [];
          }
          stockPricesData[item.variable].push({
            date: item.Date,
            price: item.value,
          });
        });
        setStockPrices(stockPricesData);

        // Fetch performance data for large charts
        const performanceResponse = await axios.get(
          "http://127.0.0.1:8000/portfolio/performance"
        );
        setNormalizedPrices(performanceResponse.data.normalized_prices);
        setRiskReturnData(performanceResponse.data.risk_return_data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchPortfolioData();
  }, []);

  const handleSendMessage = async () => {
    if (inputValue.trim() === "") return;

    // Add user message to messages state
    setMessages((prevMessages) => [
      ...prevMessages,
      { role: "user", content: inputValue },
    ]);

    try {
      // Send user message to backend
      const response = await axios.post("http://127.0.0.1:8000/chat", {
        query: inputValue,
      });

      // Add bot response to messages state
      setMessages((prevMessages) => [
        ...prevMessages,
        { role: "bot", content: response.data.answer },
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { role: "bot", content: "Sorry, I couldn't process your request." },
      ]);
    }

    // Clear input field
    setInputValue("");
  };

  const debouncedSetInputValue = useCallback(
    debounce((value: string) => setInputValue(value), 100),
    []
  );

  return (
    <div className="min-h-screen bg-[#fffff] text-[#00000]">
      {/* Top Section */}
      <div className="container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="h-16 rounded-full flex items-center justify-center">
          <img src="/Pictet.png" alt="Logo" className="h-12 object-contain" />
        </div>{" "}
        <h1 className="text-1xl font-bold">
          Interview : Master Trainee Tech Innovation
        </h1>
      </div>
      <div className="container mx-auto px-4 py-6 flex flex-col justify-center items-center">
        <h1 className="text-5xl font-bold">The Speaking Portfolio</h1>
        <p className="text-xl text-[#7a3431] mt-2">Gabriel Veigas Marques</p>
      </div>

      {/* Bottom Section - Chatbot */}
      <div className="container mx-auto px-4 py-6">
        <Card className="bg-white">
          <CardContent className="p-4">
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`flex items-end ${
                      message.role === "user" ? "flex-row-reverse" : ""
                    }`}
                  >
                    <Avatar
                      className={
                        message.role === "user" ? "bg-[#602927]" : "bg-gray-300"
                      }
                    >
                      {message.role === "user" ? (
                        <AvatarImage src="/avatar.png" />
                      ) : (
                        <AvatarImage src="/lion.png" />
                      )}
                    </Avatar>
                    <div
                      className={`mx-2 py-2 px-3 rounded-lg ${
                        message.role === "user"
                          ? "bg-[#602927] text-white"
                          : "bg-gray-200"
                      }`}
                    >
                      {message.content}
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 flex">
              <Input
                className="flex-grow mr-2"
                placeholder="Type your message..."
                defaultValue={inputValue}
                onChange={(e) => debouncedSetInputValue(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === "Enter") {
                    handleSendMessage();
                  }
                }}
              />
              <Button
                className="bg-[#602927] hover:bg-[#7a3431] text-white"
                onClick={handleSendMessage}
              >
                Send
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Portfolio Section */}
      <div className="container mx-auto px-4 py-6">
        <h2 className="text-2xl font-bold mb-4">My Portfolio</h2>
        <div className="w-full flex flex-wrap">
          {/* Left Div */}
          <div className="w-full md:w-1/2 px-2">
            <ul>
              {portfolioData.map((stock, index) => (
                <li
                  key={index}
                  className="flex justify-between py-1 border-b"
                  style={{ borderColor: "rgba(122, 52, 49, 0.2)" }}
                >
                  <span>{stock.name}</span>
                  <span>{stock.percentage}%</span>
                </li>
              ))}
            </ul>
          </div>
          {/* Right Div */}
          <div className="w-full md:w-1/2 px-2 flex items-center justify-center">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={portfolioData}
                  dataKey="percentage"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  fill="#8884d8"
                  label={({ name }) => name}
                  legendType="none"
                >
                  {portfolioData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Metrics Section */}
      <div className="container mx-auto px-4 py-6">
        {metricsData && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Basic Metrics Card */}
            <Card className="bg-white">
              <CardContent className="p-4">
                <h3 className="text-xl font-bold mb-4 text-[#602927]">
                  Basic Metrics
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(metricsData.basic_metrics).map(
                    ([key, value]) => (
                      <div key={key} className="border-b border-gray-200 py-2">
                        <p className="text-sm text-gray-600">{key}</p>
                        <p className="text-lg font-semibold">
                          {typeof value === "number"
                            ? key.includes("Drawdown")
                              ? `${(value * 100).toFixed(2)}%`
                              : value.toFixed(3)
                            : value}
                        </p>
                      </div>
                    )
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Risk Metrics Card */}
            <Card className="bg-white">
              <CardContent className="p-4">
                <h3 className="text-xl font-bold mb-4 text-[#602927]">
                  Risk Metrics
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(metricsData.risk_metrics).map(
                    ([key, value]) => (
                      <div key={key} className="border-b border-gray-200 py-2">
                        <p className="text-sm text-gray-600">{key}</p>
                        <p className="text-lg font-semibold">
                          {value.toFixed(3)}
                        </p>
                      </div>
                    )
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>

      {/* Charts Section */}
      <div className="container mx-auto px-4 py-6">
        <h2 className="text-2xl font-bold mb-4">Stock Prices</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.keys(stockPrices).map((stockName, i) => (
            <Card key={i} className="bg-white">
              <CardContent className="p-4">
                <h3 className="text-center font-bold mb-2">{stockName}</h3>
                <div className="h-[200px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={stockPrices[stockName]}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <Line
                        type="monotone"
                        dataKey="price"
                        stroke="#602927"
                        dot={false}
                      />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Portfolio Analysis Chart */}
      <div className="container mx-auto px-4 py-6">
        <h2 className="text-2xl font-bold mb-4">Portfolio Performance</h2>
        <Card className="bg-white">
          <CardContent className="p-4">
            <h3 className="text-center font-bold mb-4">
              Portfolio Performance (Normalized to 100)
            </h3>
            <div className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                {normalizedPrices.length > 0 ? (
                  <LineChart data={normalizedPrices}>
                    {Object.keys(normalizedPrices[0])
                      .filter((key) => key !== "date")
                      .map((stockName, index) => (
                        <Line
                          key={index}
                          type="monotone"
                          dataKey={stockName}
                          stroke={`hsl(${(index * 50) % 360}, 70%, 50%)`}
                          dot={false}
                        />
                      ))}
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                  </LineChart>
                ) : (
                  <div>No data available</div>
                )}
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Risk Analysis Chart */}
      <div className="container mx-auto px-4 py-6">
        <h2 className="text-2xl font-bold mb-4">Risk-Return Analysis</h2>
        <Card className="bg-white">
          <CardContent className="p-4">
            <h3 className="text-center font-bold mb-4">
              Risk-Return Scatter Plot
            </h3>
            <div className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart>
                  <CartesianGrid />
                  <XAxis
                    type="number"
                    dataKey="annualVolatility"
                    name="Annual Volatility"
                    unit=""
                    label={{
                      value: "Annual Volatility",
                      position: "insideBottom",
                      offset: -5,
                    }}
                  />
                  <YAxis
                    type="number"
                    dataKey="annualReturn"
                    name="Annual Return"
                    unit=""
                    label={{
                      value: "Annual Return",
                      angle: -90,
                      position: "insideLeft",
                      offset: 10,
                    }}
                  />
                  <Tooltip cursor={{ strokeDasharray: "3 3" }} />
                  <Scatter
                    data={riskReturnData.concat([
                      {
                        stock: "PORTFOLIO",
                        annualReturn: 0.2,
                        annualVolatility: 0.176,
                      },
                    ])}
                    fill="#602927"
                  >
                    <LabelList dataKey="stock" position="top" />
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
