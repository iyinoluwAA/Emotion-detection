import React from "react";
import {
  Container,
  Title,
  Text,
  Button,
  Group,
  Stack,
  Box,
  Grid,
  Card,
  ThemeIcon,
  Anchor,
  Paper,
  useMantineColorScheme,
} from "@mantine/core";
import {
  IconBrain,
  IconRocket,
  IconShield,
  IconBolt,
  IconChartBar,
  IconUsers,
  IconSchool,
  IconHeartHandshake,
  IconShoppingCart,
  IconTrendingUp,
  IconAccessible,
  IconArrowRight,
} from "@tabler/icons-react";
import { useNavigate } from "react-router-dom";
import { ActionToggle } from "@/components/ColorSchemeToggle/ActionToggle";
import logo from "@/assets/Emotion-detection logo.png";

const features = [
  {
    icon: IconBrain,
    title: "State-of-the-Art AI",
    description: "Two powerful models available: Base Model (92.2% accuracy) for general use, and Asripa (fine-tuned on FER2013) for enhanced emotion detection. Asripa addresses occasional misclassifications in the base model, providing more reliable results.",
    color: "violet",
  },
  {
    icon: IconBolt,
    title: "Lightning Fast",
    description: "Sub-500ms response time. Real-time emotion detection that scales with your needs.",
    color: "yellow",
  },
  {
    icon: IconShield,
    title: "Privacy-Focused",
    description: "Your data stays secure. Can be deployed on-premise. GDPR compliant architecture.",
    color: "green",
  },
  {
    icon: IconChartBar,
    title: "Analytics Built-In",
    description: "Track emotion patterns over time. Export data for analysis. Comprehensive logging.",
    color: "blue",
  },
  {
    icon: IconRocket,
    title: "Easy Integration",
    description: "Simple REST API. Works with any language. Comprehensive documentation included.",
    color: "orange",
  },
  {
    icon: IconUsers,
    title: "Production Ready",
    description: "99.9% uptime. Robust error handling. Rate limiting. Built for scale.",
    color: "pink",
  },
];

const useCases = [
  {
    icon: IconUsers,
    title: "HR & Recruitment",
    description: "Analyze candidate engagement during video interviews. Identify best-fit candidates.",
    color: "blue",
  },
  {
    icon: IconSchool,
    title: "EdTech Platforms",
    description: "Monitor student engagement in online learning. Identify when students need help.",
    color: "violet",
  },
  {
    icon: IconHeartHandshake,
    title: "Mental Health Apps",
    description: "Track emotional patterns for therapy and wellness. Help users understand their states.",
    color: "pink",
  },
  {
    icon: IconShoppingCart,
    title: "Customer Experience",
    description: "Analyze customer satisfaction in retail. Measure emotional responses to products.",
    color: "orange",
  },
  {
    icon: IconTrendingUp,
    title: "Market Research",
    description: "Measure emotional responses to products, ads, and campaigns. Get real-time feedback.",
    color: "green",
  },
  {
    icon: IconAccessible,
    title: "Accessibility",
    description: "Help people recognize emotions. Assistive technology for social interaction.",
    color: "teal",
  },
];

const stats = [
  { value: "92.2%", label: "Base Model Accuracy" },
  { value: "⭐ Asripa", label: "Enhanced Emotion Detection" },
  { value: "8", label: "Emotions Detected" },
  { value: "<500ms", label: "Response Time" },
];

export function LandingPage() {
  const navigate = useNavigate();
  const { colorScheme } = useMantineColorScheme();

  return (
    <Box 
      style={{ minHeight: "100vh" }}
      bg={colorScheme === "dark" ? "dark.8" : "white"}
    >
      {/* Dark Mode Toggle - Fixed Position */}
      <Box
        style={{
          position: "fixed",
          top: 20,
          right: 20,
          zIndex: 1000,
        }}
      >
        <ActionToggle />
      </Box>

      {/* Hero Section */}
      <Box
        style={{
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <Container size="xl" py={{ base: 60, md: 100 }}>
          <Stack gap="xl" align="center" style={{ position: "relative", zIndex: 1 }}>
            <Group gap="md" align="center" justify="center">
              <Box
                style={{
                  width: 80,
                  height: 80,
                  borderRadius: 16,
                  overflow: "hidden",
                  boxShadow: "0 8px 24px rgba(0,0,0,0.2)",
                }}
              >
                <img
                  src={logo}
                  alt="Emotion Detection Logo"
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                />
              </Box>
              <Title
                order={1}
                c="white"
                fw={800}
                ta="center"
                style={{ 
                  textShadow: "2px 2px 4px rgba(0,0,0,0.2)",
                  fontSize: "clamp(2rem, 5vw, 3.5rem)"
                }}
              >
                AI-Powered Emotion Detection
              </Title>
            </Group>
            <Text
              size="lg"
              c="white"
              ta="center"
              maw={800}
              style={{ opacity: 0.95, fontSize: "clamp(1rem, 2vw, 1.25rem)" }}
            >
              Production-ready emotion detection API with state-of-the-art accuracy. 
              Choose between our Base Model (92.2% accuracy) or Asripa — our fine-tuned model that addresses occasional misclassifications for more reliable emotion detection.
            </Text>
            <Group gap="md" justify="center" wrap="wrap">
              <Button
                size="lg"
                variant="white"
                color="violet"
                rightSection={<IconArrowRight size={20} />}
                onClick={() => navigate("/app")}
              >
                Try Live Demo
              </Button>
              <Button
                size="lg"
                variant="outline"
                color="white"
                onClick={() => {
                  document.getElementById("features")?.scrollIntoView({ behavior: "smooth" });
                }}
              >
                Learn More
              </Button>
            </Group>
          </Stack>
        </Container>
      </Box>

      {/* Stats Section */}
      <Container size="xl" py={{ base: 40, md: 60 }}>
        <Grid gutter="md">
          {stats.map((stat, index) => (
            <Grid.Col key={index} span={{ base: 6, sm: 3 }}>
              <Paper p="md" withBorder radius="md" ta="center">
                <Text size="xl" fw={700} c="violet">
                  {stat.value}
                </Text>
                <Text size="sm" c="dimmed" mt={4}>
                  {stat.label}
                </Text>
              </Paper>
            </Grid.Col>
          ))}
        </Grid>
      </Container>

      {/* Features Section */}
      <Box 
        id="features" 
        bg={colorScheme === "dark" ? "dark.7" : "gray.0"} 
        py={{ base: 60, md: 80 }}
      >
        <Container size="xl">
          <Stack gap="xl">
            <Box ta="center">
              <Title order={2} mb="md" style={{ fontSize: "clamp(1.75rem, 4vw, 2.625rem)" }}>
                Why Choose Our Emotion Detection API?
              </Title>
              <Text size="lg" c="dimmed" maw={600} mx="auto">
                Built with cutting-edge AI technology and designed for real-world applications
              </Text>
            </Box>
            <Grid gutter="lg">
              {features.map((feature, index) => (
                <Grid.Col key={index} span={{ base: 12, sm: 6, md: 4 }}>
                  <Card shadow="sm" padding="lg" radius="md" withBorder h="100%">
                    <Stack gap="md">
                      <ThemeIcon size={60} radius="md" variant="light" color={feature.color}>
                        <feature.icon size={30} />
                      </ThemeIcon>
                      <Title order={4}>{feature.title}</Title>
                      <Text size="sm" c="dimmed">
                        {feature.description}
                      </Text>
                    </Stack>
                  </Card>
                </Grid.Col>
              ))}
            </Grid>
          </Stack>
        </Container>
      </Box>

      {/* Use Cases Section */}
      <Box bg={colorScheme === "dark" ? "dark.8" : "transparent"}>
        <Container size="xl" py={{ base: 60, md: 80 }}>
        <Stack gap="xl">
          <Box ta="center">
            <Title order={2} mb="md" style={{ fontSize: "clamp(1.75rem, 4vw, 2.625rem)" }}>
              Perfect For These Use Cases
            </Title>
            <Text size="lg" c="dimmed" maw={600} mx="auto">
              From HR to healthcare, our API powers emotion detection across industries
            </Text>
          </Box>
          <Grid gutter="lg">
            {useCases.map((useCase, index) => (
              <Grid.Col key={index} span={{ base: 12, sm: 6, md: 4 }}>
                <Card shadow="sm" padding="lg" radius="md" withBorder h="100%">
                  <Stack gap="md">
                    <Group gap="md">
                      <ThemeIcon size={50} radius="md" variant="light" color={useCase.color}>
                        <useCase.icon size={24} />
                      </ThemeIcon>
                      <Title order={4} style={{ flex: 1 }}>
                        {useCase.title}
                      </Title>
                    </Group>
                    <Text size="sm" c="dimmed">
                      {useCase.description}
                    </Text>
                  </Stack>
                </Card>
              </Grid.Col>
            ))}
          </Grid>
        </Stack>
      </Container>
      </Box>

      {/* CTA Section */}
      <Box
        style={{
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        }}
        py={{ base: 60, md: 80 }}
      >
        <Container size="xl">
          <Stack gap="xl" align="center" ta="center">
            <Title order={2} c="white" style={{ fontSize: "clamp(1.75rem, 4vw, 2.625rem)" }}>
              Ready to Get Started?
            </Title>
            <Text size="lg" c="white" maw={600} style={{ opacity: 0.95 }}>
              Try our emotion detection API today. No credit card required. 
              Upload an image and see the magic happen.
            </Text>
            <Group gap="md" justify="center">
              <Button
                size="lg"
                variant="white"
                color="violet"
                rightSection={<IconArrowRight size={20} />}
                onClick={() => navigate("/app")}
              >
                Start Detecting Emotions
              </Button>
            </Group>
          </Stack>
        </Container>
      </Box>

      {/* Footer */}
      <Box bg={colorScheme === "dark" ? "dark.9" : "dark.9"} py="xl">
        <Container size="xl">
          <Stack gap="md" align="center">
            <Text c="dimmed" size="sm" ta="center">
              © 2025 Emotion Detection API. Built with ❤️ for developers.
            </Text>
            <Group gap="lg">
              <Anchor
                href="https://github.com/iyinoluwAA/Emotion-detection"
                target="_blank"
                c="dimmed"
                size="sm"
              >
                GitHub
              </Anchor>
              <Text c="dimmed" size="sm">
                •
              </Text>
              <Anchor
                href="https://huggingface.co"
                target="_blank"
                c="dimmed"
                size="sm"
              >
                Powered by HuggingFace
              </Anchor>
            </Group>
          </Stack>
        </Container>
      </Box>
    </Box>
  );
}

