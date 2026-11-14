// Copyright 2026 Kartikay Srivastava. SPDX-License-Identifier: Apache-2.0
#include <algorithm>
#include <charconv>
#include <cmath>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

int Parse(const char * text)
{
  const std::string value(text);
  int result = 0;
  const auto parsed = std::from_chars(value.data(), value.data() + value.size(), result);
  if (parsed.ec != std::errc{} || parsed.ptr != value.data() + value.size())
  {
    throw std::invalid_argument("Expected an integer");
  }
  return result;
}

int main(int argc, char ** argv)
{
  try
  {
    if (argc != 7) { throw std::invalid_argument("Expected operation, width, height, amount, seedX, seedY"); }
    const std::string operation(argv[1]);
    const int width = Parse(argv[2]), height = Parse(argv[3]), amount = Parse(argv[4]);
    const int seedX = Parse(argv[5]), seedY = Parse(argv[6]);
    if (width < 1 || height < 1 || width > 1024 || height > 1024 || amount < 0 || amount > 255 ||
        seedX < 0 || seedY < 0 || seedX >= width || seedY >= height)
    {
      throw std::invalid_argument("Parameters outside supported range");
    }
    const int count = width * height;
    std::vector<unsigned char> input(count), output(count);
    std::cin.read(reinterpret_cast<char *>(input.data()), count);
    if (std::cin.gcount() != count || std::cin.peek() != std::char_traits<char>::eof())
    {
      throw std::invalid_argument("Pixel buffer size mismatch");
    }
    if (operation == "threshold")
    {
      for (int i = 0; i < count; ++i) { output[i] = input[i] >= amount ? 255 : 0; }
    }
    else if (operation == "region")
    {
      const int seed = seedY * width + seedX;
      std::vector<int> pending{ seed };
      output[seed] = 255;
      for (std::size_t cursor = 0; cursor < pending.size(); ++cursor)
      {
        const int current = pending[cursor], x = current % width, y = current / width;
        const int neighbors[] = { x > 0 ? current - 1 : -1, x + 1 < width ? current + 1 : -1,
                                  y > 0 ? current - width : -1, y + 1 < height ? current + width : -1 };
        for (const int next : neighbors)
        {
          if (next >= 0 && output[next] == 0 && std::abs(int(input[next]) - int(input[seed])) <= amount)
          {
            output[next] = 255;
            pending.push_back(next);
          }
        }
      }
    }
    else if (operation == "noise")
    {
      std::mt19937 random(42);
      std::normal_distribution<double> noise(0.0, 1.0);
      for (int i = 0; i < count; ++i)
      {
        output[i] = static_cast<unsigned char>(std::clamp(std::lround(input[i] + amount * noise(random)), 0L, 255L));
      }
    }
    else if (operation == "smooth")
    {
      const int radius = std::min(amount, 8);
      const int stride = width + 1;
      std::vector<unsigned int> integral((width + 1) * (height + 1), 0);
      for (int y = 0; y < height; ++y)
      {
        unsigned int row = 0;
        for (int x = 0; x < width; ++x)
        {
          row += input[y * width + x];
          integral[(y + 1) * stride + x + 1] = integral[y * stride + x + 1] + row;
        }
      }
      for (int y = 0; y < height; ++y)
      {
        for (int x = 0; x < width; ++x)
        {
          const int left = std::max(0, x - radius), right = std::min(width, x + radius + 1);
          const int top = std::max(0, y - radius), bottom = std::min(height, y + radius + 1);
          const auto sum = integral[bottom * stride + right] + integral[top * stride + left] -
                           integral[top * stride + right] - integral[bottom * stride + left];
          output[y * width + x] = static_cast<unsigned char>(sum / ((right - left) * (bottom - top)));
        }
      }
    }
    else { throw std::invalid_argument("Unknown operation"); }
    std::cout.write(reinterpret_cast<const char *>(output.data()), count);
    return std::cout ? 0 : 1;
  }
  catch (const std::exception & error)
  {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
