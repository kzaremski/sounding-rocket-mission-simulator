// Packages
const path = require('path');

module.exports = {
  module:{
    rules:[
      {
        test:/\.(js|jsx|ts|tsx)$/,
        exclude:/node_modules/,
        use: {
          loader:'babel-loader',
        },
      },
      {
        test: /\.css$/i,
        use: ["style-loader", "css-loader"],
      },
    ]
  },
  entry: {
    main: path.resolve(__dirname, "src/main.jsx"),
  },
  output: {
    path: path.resolve(__dirname, "static", "build"),
    filename: "[name].js"
  },
  resolve: {
    extensions: ['.js', '.jsx', '.ts', '.tsx'],
  }
};