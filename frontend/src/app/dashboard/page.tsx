"use client";

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

export default function Dashboard() {
  const [messages, setMessages] = useState([
    { role: "bot", content: "Hello! How can I assist you today?" },
    {
      role: "user",
      content: "Can you tell me about the data in these charts?",
    },
    {
      role: "bot",
      content:
        "The charts display various metrics and trends. Which specific chart would you like me to explain?",
    },
  ]);

  return (
    <div className="min-h-screen bg-[#fffff] text-[#00000]">
      {/* Top Section */}
      <div className="container mx-auto px-4 py-6 flex justify-between items-center">
        <div className="h-16 rounded-full flex items-center justify-center">
          <img src="/Pictet.png" alt="Logo" className="h-12 object-contain" />
        </div>{" "}
        <h1 className="text-3xl font-bold">
          Interview : Master Trainee Tech Innovation
        </h1>
      </div>
      <div className="container mx-auto px-4 py-6 flex justify-center items-center">
        <h1 className="text-5xl font-bold">The Speaking Portfolio</h1>
      </div>

      {/* Middle Section - Carousel */}
      <div className="container mx-auto px-4 py-6">
        <Carousel className="w-full">
          <CarouselContent>
            {/* First Layout - 12 small charts */}
            <CarouselItem>
              <div className="grid grid-cols-2 gap-4">
                {[...Array(12)].map((_, i) => (
                  <Card key={i} className="bg-white">
                    <CardContent className="p-4">
                      <div className="h-[200px] bg-gray-100 flex items-center justify-center">
                        Chart {i + 1} Placeholder
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CarouselItem>
            {/* Second Layout - Single large chart */}
            <CarouselItem>
              <Card className="bg-white">
                <CardContent className="p-4">
                  <div className="h-[600px] bg-gray-100 flex items-center justify-center">
                    Large Chart 1 Placeholder
                  </div>
                </CardContent>
              </Card>
            </CarouselItem>
            {/* Third Layout - Another single large chart */}
            <CarouselItem>
              <Card className="bg-white">
                <CardContent className="p-4">
                  <div className="h-[600px] bg-gray-100 flex items-center justify-center">
                    Large Chart 2 Placeholder
                  </div>
                </CardContent>
              </Card>
            </CarouselItem>
          </CarouselContent>
          <CarouselPrevious />
          <CarouselNext />
        </Carousel>
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
                      <AvatarFallback>
                        {message.role === "user" ? "U" : "B"}
                      </AvatarFallback>
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
              />
              <Button className="bg-[#602927] hover:bg-[#7a3431] text-white">
                Send
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
