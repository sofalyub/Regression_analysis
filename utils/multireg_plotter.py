"""
Improved module for plotting multiple regression plots with better text handling
"""

import matplotlib.pyplot as plt
import numpy as np
import traceback
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.ticker import FuncFormatter, MaxNLocator
from utils.base_plotter import BasePlotter, HAS_AXES_GRID, HAS_3D, HAS_SKLEARN

# Import additional libraries if available
if HAS_AXES_GRID:
    from mpl_toolkits.axes_grid1 import make_axes_locatable

if HAS_3D:
    from mpl_toolkits.mplot3d import Axes3D

if HAS_SKLEARN:
    from sklearn.preprocessing import StandardScaler


class MultiRegPlotter(BasePlotter):
    """
    Improved class for plotting multiple regression with better text handling
    """
    
    @staticmethod
    def number_formatter(x, pos):
        """
        Formats numbers for better display
        
        Args:
            x: Number to format
            pos: Position (required for FuncFormatter)
            
        Returns:
            str: Formatted number
        """
        if abs(x) >= 1e6:
            return f'{x/1e6:.1f} млн'
        elif abs(x) >= 1e3:
            return f'{x/1e3:.1f} тыс'
        else:
            return f'{x:.1f}'
    
    @staticmethod
    def shorten_name(name, max_length=15):
        """
        Shortens a long name to the specified length
        
        Args:
            name (str): Name to shorten
            max_length (int): Maximum length of result
            
        Returns:
            str: Shortened name
        """
        if len(name) <= max_length:
            return name
            
        words = name.split()
        if len(words) > 1:
            # Take first word + first letters of following words
            short_name = words[0]
            if len(short_name) > max_length - 4:  # Leave space for "..."
                short_name = short_name[:max_length-4] + "..."
            else:
                remaining_length = max_length - len(short_name) - 3  # -3 for "..."
                if remaining_length > 0:
                    # Add initials of following words
                    initials = ''.join([word[0] for word in words[1:] if word])[:remaining_length]
                    if initials:
                        short_name += " " + initials + "..."
                    else:
                        short_name += "..."
        else:
            # One long word - just truncate
            short_name = name[:max_length-3] + "..."
            
        return short_name
    
    @staticmethod
    def create_prediction_vs_actual_plot(X, y, model, y_label="Y", title="Прогноз vs Факт"):
        """
        Creates predicted vs actual values plot
        
        Args:
            X (numpy.ndarray): Array of independent variables
            y (numpy.ndarray): Array of dependent variable
            model: Regression model with predict method
            y_label (str): Label for Y axis
            title (str): Plot title
            
        Returns:
            FigureCanvas: Plot object
        """
        try:
            # Create figure with improved size for accommodating long text
            fig = Figure(figsize=(14, 10))
            canvas = FigureCanvas(fig)
            
            # Improve margins for text accommodation
            ax = fig.add_subplot(111)
            fig.subplots_adjust(top=0.85, bottom=0.15, left=0.15, right=0.9, hspace=0.3)
            
            # Get predicted values
            predictions = model.predict(X)
            
            # Determine appropriate marker size
            marker_size = max(20, min(80, 2000 / len(X)))  # Slightly reduced marker size
            
            # Plot points with color gradient by y values
            scatter = ax.scatter(predictions, y, c=y, cmap='viridis', 
                                 s=marker_size, alpha=0.7, edgecolors='navy')
            
            # Add color bar
            try:
                cb = fig.colorbar(scatter, ax=ax, pad=0.02)
                # Use full text for color bar label, not shortened
                cb.set_label(y_label, fontsize=10)
            except Exception as e:
                print(f"Could not add colorbar: {e}")
            
            # Add y=x line (perfect predictions)
            min_val = min(min(predictions), min(y))
            max_val = max(max(predictions), max(y))
            margin = (max_val - min_val) * 0.05
            line_range = np.array([min_val - margin, max_val + margin])
            ax.plot(line_range, line_range, color='red', linestyle='--', linewidth=2)
            
            # Add model quality information
            r2_str = f"{model.r_squared:.4f}".replace('.', ',')
            adj_r2_str = f"{model.adjusted_r_squared:.4f}".replace('.', ',')
            text_box = ax.text(0.02, 0.95, 
                             f"R² = {r2_str}\nСкорр. R² = {adj_r2_str}", 
                             transform=ax.transAxes, fontsize=12, 
                             verticalalignment='top', 
                             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
            
            # Configure axes and title - use unwrapped titles
            ax.set_title(MultiRegPlotter._break_long_text(title, 60), fontweight='bold', fontsize=14, pad=20)
            
            ax.set_xlabel("Прогнозируемые значения", fontweight='bold', fontsize=12)
            ax.set_ylabel("Фактические значения", fontweight='bold', fontsize=12)
            
            # Improved axis formatting for large numbers
            ax.xaxis.set_major_formatter(FuncFormatter(MultiRegPlotter.number_formatter))
            ax.yaxis.set_major_formatter(FuncFormatter(MultiRegPlotter.number_formatter))
            
            # Reduce number of ticks on axes
            ax.xaxis.set_major_locator(MaxNLocator(5))
            ax.yaxis.set_major_locator(MaxNLocator(5))
            
            # Set optimal plot boundaries
            ax.set_xlim(min_val - margin, max_val + margin)
            ax.set_ylim(min_val - margin, max_val + margin)
            
            # Add grid
            ax.grid(True, linestyle='--', alpha=0.7)
            
            return canvas
            
        except Exception as e:
            print(f"Error creating Prediction vs Actual plot: {e}")
            traceback.print_exc()
            
            # Create empty plot with error message
            fig = Figure(figsize=(10, 6))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, f"Error creating plot: {str(e)}", 
                    ha='center', va='center', transform=ax.transAxes, color='red')
            return canvas
    
    @staticmethod
    def create_residuals_plot(X, y, model, y_label="Y", title="График остатков"):
        """
        Creates an improved residuals plot
        
        Args:
            X (numpy.ndarray): Array of independent variables
            y (numpy.ndarray): Array of dependent variable
            model: Regression model
            y_label (str): Label for Y axis
            title (str): Plot title
            
        Returns:
            FigureCanvas: Plot object
        """
        try:
            # Create figure with improved size
            fig = Figure(figsize=(14, 10))
            canvas = FigureCanvas(fig)
            
            # Optimize margins for long labels and titles
            fig.subplots_adjust(top=0.85, bottom=0.15, left=0.15, right=0.85, hspace=0.3)
            
            ax = fig.add_subplot(111)
            
            # Get predicted values
            predictions = model.predict(X)
            
            # Calculate residuals
            residuals = y - predictions
            
            # Determine appropriate marker size
            marker_size = max(20, min(80, 2000 / len(X)))
            
            # Plot residuals with color gradient
            scatter = ax.scatter(predictions, residuals, 
                                c=np.abs(residuals), cmap='coolwarm', 
                                s=marker_size, alpha=0.7, edgecolors='darkgreen')
            
            # Add color bar
            try:
                cb = fig.colorbar(scatter, ax=ax, pad=0.02)
                cb.set_label('|Остаток|', fontsize=10)
            except Exception as e:
                print(f"Could not add colorbar: {e}")
            
            # Add horizontal line at y=0
            ax.axhline(y=0, color='red', linestyle='-', linewidth=2, zorder=3)
            
            # Add residual statistics
            mean_residual = np.mean(residuals)
            std_residual = np.std(residuals)
            
            stats_text = (f"Среднее значение остатков: {mean_residual:.4f}\n"
                          f"Стандартное отклонение: {std_residual:.4f}")
            
            # Place information in a box
            text_box = ax.text(0.02, 0.95, stats_text, 
                             transform=ax.transAxes, fontsize=12, 
                             verticalalignment='top', 
                             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
            
            # Add residuals histogram on the right if axes_grid1 is available
            if HAS_AXES_GRID:
                try:
                    divider = make_axes_locatable(ax)
                    ax_histy = divider.append_axes("right", 1.0, pad=0.2)  # Increased padding
                    ax_histy.hist(residuals, bins=min(10, len(residuals)//5 + 2),
                                orientation='horizontal', color='green', alpha=0.6)
                    ax_histy.axhline(y=0, color='red', linestyle='-', linewidth=2)
                    ax_histy.set_xticks([])
                    ax_histy.set_yticks([])
                    ax_histy.spines['right'].set_visible(False)
                    ax_histy.spines['top'].set_visible(False)
                    ax_histy.spines['bottom'].set_visible(False)
                except Exception as e:
                    print(f"Could not add histogram: {e}")
            
            # Configure axes and title - use wrapped title for better display
            ax.set_title(MultiRegPlotter._break_long_text(title, 60), 
                        fontweight='bold', fontsize=14, pad=20)
            
            ax.set_xlabel("Прогнозируемые значения", fontweight='bold', fontsize=12)
            ax.set_ylabel("Остатки", fontweight='bold', fontsize=12)
            
            # Improved formatting for large numbers
            ax.xaxis.set_major_formatter(FuncFormatter(MultiRegPlotter.number_formatter))
            
            # Reduce number of ticks on axes
            ax.xaxis.set_major_locator(MaxNLocator(5))
            ax.yaxis.set_major_locator(MaxNLocator(5))
            
            # Set symmetric Y limits relative to zero
            max_abs_residual = max(abs(np.max(residuals)), abs(np.min(residuals)))
            y_margin = max_abs_residual * 0.1
            ax.set_ylim(-max_abs_residual - y_margin, max_abs_residual + y_margin)
            
            # Add grid
            ax.grid(True, linestyle='--', alpha=0.7)
            
            return canvas
            
        except Exception as e:
            print(f"Error creating residuals plot: {e}")
            traceback.print_exc()
            
            # Create empty plot with error message
            fig = Figure(figsize=(10, 6))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, f"Error creating residuals plot: {str(e)}", 
                    ha='center', va='center', transform=ax.transAxes, color='red')
            return canvas
    
    @staticmethod
    def create_correlation_matrix(data, feature_names, title="Корреляционная матрица"):
        """
        Creates an improved correlation matrix with better handling of long labels
        
        Args:
            data (numpy.ndarray): Data for correlation
            feature_names (list): List of feature names
            title (str): Plot title
            
        Returns:
            FigureCanvas: Plot object
        """
        try:
            # Calculate correlation matrix
            corr_matrix = np.corrcoef(data.T)
            
            # Create figure with increased size for long labels
            fig = Figure(figsize=(16, 14))
            canvas = FigureCanvas(fig)
            
            # Significantly increase margins for long labels
            # ИЗМЕНЕНИЕ: Уменьшаем top с 0.85 до 0.75, чтобы увеличить промежуток между заголовком и матрицей
            fig.subplots_adjust(left=0.35, right=0.85, bottom=0.35, top=0.75)
            
            ax = fig.add_subplot(111)
            
            # Plot heatmap
            cmap = plt.cm.coolwarm
            im = ax.imshow(corr_matrix, cmap=cmap, vmin=-1, vmax=1)
            
            # Add colorbar
            cb = fig.colorbar(im, ax=ax, shrink=0.8)
            cb.set_label('Коэффициент корреляции', fontsize=12)
            
            # Add correlation values to cells
            for i in range(len(corr_matrix)):
                for j in range(len(corr_matrix)):
                    # Determine text color based on correlation value
                    text_color = 'white' if abs(corr_matrix[i, j]) > 0.5 else 'black'
                    # Format number
                    ax.text(j, i, f"{corr_matrix[i, j]:.2f}",
                        ha="center", va="center", color=text_color, fontsize=11)
            
            # Configure axes
            ax.set_xticks(np.arange(len(feature_names)))
            ax.set_yticks(np.arange(len(feature_names)))
            
            # *** IMPROVED: Better handle long feature names ***
            wrapped_feature_names = [MultiRegPlotter._break_long_text(name, 25) for name in feature_names]
            
            # Rotate y-axis labels for better readability
            ax.set_yticklabels(wrapped_feature_names, fontsize=9)
            
            # Set x-axis labels with appropriate rotation and position
            ax.set_xticklabels(wrapped_feature_names, rotation=45, ha="right", fontsize=9)
            
            # Set title
            wrapped_title = MultiRegPlotter._break_long_text(title, 40)
            # ИЗМЕНЕНИЕ: Увеличиваем pad с 20 до 40 для большего промежутка между заголовком и матрицей
            ax.set_title(wrapped_title, fontweight='bold', fontsize=14, pad=40)
            
            # Adjust bottom margin to accommodate rotated x labels
            fig.subplots_adjust(bottom=0.4)
            
            # Adjust left margin for long y labels
            fig.subplots_adjust(left=0.35)
            
            return canvas
            
        except Exception as e:
            print(f"Error creating correlation matrix: {e}")
            traceback.print_exc()
            
            # Create empty plot with error message
            fig = Figure(figsize=(10, 6))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, f"Error creating correlation matrix: {str(e)}", 
                    ha='center', va='center', transform=ax.transAxes, color='red')
            return canvas
        
    @staticmethod
    def _split_name(name, max_width=20):
        """
        Splits a long name into multiple lines for better display
        
        Args:
            name (str): Name to split
            max_width (int): Maximum width of line
        
        Returns:
            list: List of lines
        """
        if len(name) <= max_width:
            return [name]
        
        words = name.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= max_width:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # If text contains no spaces, force split it
        if not lines:
            return [name[:max_width], name[max_width:]]
            
        return lines
    
    @staticmethod
    def create_3d_surface_plot(X, y, model, x1_index, x2_index, feature_names, y_label, title):
        """
        Creates a 3D surface plot for two selected features with improved text positioning
        
        Args:
            X (numpy.ndarray): Array of independent variables
            y (numpy.ndarray): Array of dependent variable
            model: Regression model
            x1_index (int): Index of first feature
            x2_index (int): Index of second feature
            feature_names (list): List of feature names
            y_label (str): Label for Y axis
            title (str): Plot title
            
        Returns:
            FigureCanvas: Plot object
        """
        if not HAS_3D:
            fig = Figure(figsize=(10, 6))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "3D plots require mpl_toolkits.mplot3d", 
                    ha='center', va='center', transform=ax.transAxes, color='red')
            return canvas
            
        try:
            # Create 3D plot with increased size for text accommodation
            fig = Figure(figsize=(18, 14))
            canvas = FigureCanvas(fig)
            
            # Configure margins for better use of space
            fig.subplots_adjust(left=0.1, right=0.9, bottom=0.15, top=0.9)
            
            ax = fig.add_subplot(111, projection='3d')
            
            # Get data for plot
            x1_data = X[:, x1_index]
            x2_data = X[:, x2_index]
            
            # Normalize data for better display, if StandardScaler is available
            x1_norm, x2_norm = x1_data, x2_data
            
            if HAS_SKLEARN:
                try:
                    scaler = StandardScaler()
                    x1_norm = scaler.fit_transform(x1_data.reshape(-1, 1)).flatten()
                    x2_norm = scaler.fit_transform(x2_data.reshape(-1, 1)).flatten()
                except Exception as e:
                    print(f"Could not normalize data: {e}")
            
            # Plot 3D-scatter with color gradient by y value
            scatter = ax.scatter(x1_norm, x2_norm, y, 
                            c=y, cmap='viridis', 
                            s=40, alpha=0.7, edgecolors='navy')
            
            # Add colorbar with better positioning
            try:
                # Увеличиваем pad для создания отступа слева от шкалы цвета
                cb = fig.colorbar(scatter, ax=ax, pad=0.15, shrink=0.4, aspect=10)
                # Добавляем отступ для текста на шкале цвета
                cb_label = MultiRegPlotter._break_long_text(y_label, 15)
                cb.set_label(cb_label, fontsize=8, labelpad=15)  # Уменьшаем размер текста с 10 до 8
            except Exception as e:
                print(f"Could not add colorbar: {e}")
                
            # Create grid for plotting regression surface
            x1_grid = np.linspace(min(x1_norm), max(x1_norm), 10)
            x2_grid = np.linspace(min(x2_norm), max(x2_norm), 10)
            X1_grid, X2_grid = np.meshgrid(x1_grid, x2_grid)
            
            # Prepare points for predictions
            grid_points = np.column_stack([X1_grid.flatten(), X2_grid.flatten()])
            
            # Transform grid back to original scale, if normalized
            grid_x1_orig, grid_x2_orig = grid_points[:, 0], grid_points[:, 1]
            
            if HAS_SKLEARN:
                try:
                    grid_x1_orig = scaler.inverse_transform(grid_points[:, 0].reshape(-1, 1)).flatten()
                    grid_x2_orig = scaler.inverse_transform(grid_points[:, 1].reshape(-1, 1)).flatten()
                except Exception as e:
                    print(f"Could not transform normalized data back: {e}")
            
            # Prepare full dataset for prediction
            grid_data = np.zeros((len(grid_x1_orig), X.shape[1]))
            
            # Fill with mean values for unused features
            for i in range(X.shape[1]):
                if i == x1_index:
                    grid_data[:, i] = grid_x1_orig
                elif i == x2_index:
                    grid_data[:, i] = grid_x2_orig
                else:
                    grid_data[:, i] = np.mean(X[:, i])
            
            # Get predictions for grid
            Z_pred = model.predict(grid_data).reshape(X1_grid.shape)
            
            # Plot regression surface as wireframe for lower load
            try:
                wireframe = ax.plot_wireframe(X1_grid, X2_grid, Z_pred, 
                                        color='red', alpha=0.3, linewidth=0.3)
            except Exception as e:
                print(f"Could not plot wireframe: {e}")
            
            # *** IMPROVED: Better handle long feature names ***
            # Use multi-line text formatting for all axis labels
            x1_label = MultiRegPlotter._break_long_text(feature_names[x1_index], 15)
            x2_label = MultiRegPlotter._break_long_text(feature_names[x2_index], 15)
            z_label = MultiRegPlotter._break_long_text(y_label, 15)
            
            # УЛУЧШЕНИЕ: Проверяем, содержит ли метка оси "Савокупный показатель"
            contains_savokupny = "Савокупный показатель" in feature_names[x2_index]
            
            # Устанавливаем метки осей с увеличенным отступом для оси Y при необходимости
            ax.set_xlabel(x1_label, fontsize=8, labelpad=20)  # Уменьшили размер с 10 до 8
            
            # ИЗМЕНЕНИЕ: Увеличиваем отступ для метки оси Y и меняем ориентацию текста, 
            # если есть сложное название "Савокупный показатель"
            if contains_savokupny:
                # Горизонтальная ориентация текста с большим отступом
                ax.set_ylabel(x2_label, fontsize=8, labelpad=60, rotation=0)  # Уменьшили размер с 10 до 8
            else:
                # Стандартный отступ для других случаев
                ax.set_ylabel(x2_label, fontsize=8, labelpad=30)  # Уменьшили размер с 10 до 8
            
            # FIXED: Properly set Z label with increased padding to prevent overlap
            ax.set_zlabel(z_label, fontsize=8, labelpad=40)  # Уменьшили размер с 10 до 8
            
            # Increase space for ticks to avoid overlap
            ax.tick_params(axis='x', pad=8, labelsize=7)  # Уменьшили размер с 8 до 7
            ax.tick_params(axis='y', pad=8, labelsize=7)  # Уменьшили размер с 8 до 7
            ax.tick_params(axis='z', pad=10, labelsize=7)  # Уменьшили размер с 8 до 7
            
            # Remove title from the 3D plot itself
            ax.set_title("")
            
            # ИЗМЕНЕНИЕ: Добавляем отступ слева в заголовке перед словом "Северо-Кавказский"
            # путем добавления пробелов перед текстом заголовка
            if "Северо-Кавказский" in title:
                # Добавляем отступ перед названием округа
                padding_spaces = "    "  # 4 пробела для отступа
                title = title.replace("Северо-Кавказский", f"{padding_spaces}Северо-Кавказский")
            
            # ИЗМЕНЕНИЕ: Добавляем отступ перед "Савокупный показатель" в заголовке
            if "Савокупный показатель" in title:
                padding_spaces = "    "  # 4 пробела для отступа
                title = title.replace("Савокупный показатель", f"{padding_spaces}Савокупный показатель")
            
            title_lines = MultiRegPlotter._break_long_text(title, 40)
            fig.text(0.5, 0.93, title_lines, fontsize=14, weight='bold', 
                    ha='center', va='center')
            
            # Add model information in bottom corner
            fig.text(0.05, 0.02, f"R² = {model.r_squared:.4f}", fontsize=10, 
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
            
            # Set better viewing angle for text scaling
            ax.view_init(elev=25, azim=230)  # Adjusted angle for better view
            
            # Configure axis boundaries for better scaling
            ax.set_box_aspect([1, 1, 0.7])  # Slightly higher for better proportions
            
            # Add margins to all axes for better spacing
            ax.margins(x=0.1, y=0.1, z=0.1)
            
            # Reduce number of ticks on axes and format numbers for cleaner display
            ax.xaxis.set_major_locator(MaxNLocator(4))
            ax.yaxis.set_major_locator(MaxNLocator(4))
            ax.zaxis.set_major_locator(MaxNLocator(4))
            
            return canvas
            
        except Exception as e:
            print(f"Error creating 3D plot: {e}")
            traceback.print_exc()
            
            # Create empty plot with error message
            fig = Figure(figsize=(10, 6))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, f"Error creating 3D plot: {str(e)}", 
                    ha='center', va='center', transform=ax.transAxes, color='red')
            return canvas

    @staticmethod
    def _wrap_label_for_3d(text, line_length=15):
        """
        Special formatter for 3D axis labels, using shorter lines
        and additional spacing for 3D context
        
        Args:
            text (str): Text to format
            line_length (int): Maximum line length
            
        Returns:
            str: Formatted text with line breaks
        """
        # For 3D labels, use shorter line lengths and add extra space
        # at beginning of each line after the first
        lines = []
        words = text.split()
        current_line = ""
        
        for i, word in enumerate(words):
            if len(current_line) + len(word) + 1 <= line_length:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # If no spaces in long text, force split
        if not lines and len(text) > line_length:
            for i in range(0, len(text), line_length):
                end = min(i + line_length, len(text))
                lines.append(text[i:end])
            
        # Join with newlines and add extra spacing for 3D effect
        return '\n'.join(lines)

    @staticmethod
    def _break_long_text(text, line_length=20):
        """
        Breaks long text into multiple lines
        
        Args:
            text (str): Long text
            line_length (int): Maximum length of line
            
        Returns:
            str: Text with line breaks
        """
        if len(text) <= line_length:
            return text
        
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= line_length:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # If text contains no spaces, force split it
        if not lines:
            lines = []
            for i in range(0, len(text), line_length):
                lines.append(text[i:i+line_length])
        
        return '\n'.join(lines)
    
    @staticmethod
    def create_partial_dependence_plot(X, y, model, feature_index, feature_name, y_label, title=None):
        """
        Creates an improved partial dependence plot for a specific feature
        
        Args:
            X (numpy.ndarray): Array of independent variables
            y (numpy.ndarray): Array of dependent variable
            model: Regression model
            feature_index (int): Index of feature
            feature_name (str): Name of feature
            y_label (str): Label for Y axis
            title (str, optional): Plot title
            
        Returns:
            FigureCanvas: Plot object
        """
        try:
            # Create figure with improved size for long text
            fig = Figure(figsize=(14, 10))
            canvas = FigureCanvas(fig)
            
            # Optimize margins for long labels
            fig.subplots_adjust(bottom=0.15, left=0.15, right=0.95, top=0.85)
            
            ax = fig.add_subplot(111)
            
            # Create partial dependence
            x_feature = X[:, feature_index]
            
            # Sort for better display
            sort_indices = np.argsort(x_feature)
            sorted_x = x_feature[sort_indices]
            
            # Calculate predictions when varying only this feature
            partial_predictions = []
            x_range = np.linspace(min(x_feature), max(x_feature), 100)
            
            for x_val in x_range:
                # Create copy of data
                X_temp = X.copy()
                # Change only selected feature
                X_temp[:, feature_index] = x_val
                # Get average prediction
                pred = np.mean(model.predict(X_temp))
                partial_predictions.append(pred)
            
            # Plot partial dependence line
            ax.plot(x_range, partial_predictions, color='blue', linewidth=3)
            
            # Add actual points with lower size and transparency
            ax.scatter(x_feature, y, color='gray', alpha=0.2, s=20)
            
            # Add coefficient and p-value information
            coef = model.coefficients[feature_index]
            p_value_text = ""
            if hasattr(model, 'coef_p_values') and model.coef_p_values is not None:
                p_value = model.coef_p_values[feature_index]
                p_value_str = f"{p_value:.4f}".replace('.', ',')
                significance = "значимый" if p_value < 0.05 else "незначимый"
                p_value_text = f"\np-зн = {p_value_str} ({significance})"
            
            coef_str = f"{coef:.4f}".replace('.', ',')
            text_box = ax.text(0.02, 0.95, 
                            f"Коэф = {coef_str}{p_value_text}", 
                            transform=ax.transAxes, fontsize=12, 
                            verticalalignment='top', 
                            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
            
            # Break long feature names into multiple lines
            x_label_lines = MultiRegPlotter._break_long_text(feature_name, 40)
            y_effect_text = f"Эффект на {y_label}"
            y_label_lines = MultiRegPlotter._break_long_text(y_effect_text, 40)
            
            # Use broken-line axis labels
            ax.set_xlabel(x_label_lines, fontweight='bold', fontsize=12)
            ax.set_ylabel(y_label_lines, fontweight='bold', fontsize=12)
            
            # Set title with line breaks if needed
            if title is None:
                title = f"Частичная зависимость для {feature_name}"
            
            title_lines = MultiRegPlotter._break_long_text(title, 60)
            ax.set_title(title_lines, fontweight='bold', fontsize=14, pad=20)
            
            # Improved formatting for large numbers
            ax.xaxis.set_major_formatter(FuncFormatter(MultiRegPlotter.number_formatter))
            ax.yaxis.set_major_formatter(FuncFormatter(MultiRegPlotter.number_formatter))
            
            # Reduce number of ticks on axes
            ax.xaxis.set_major_locator(MaxNLocator(5))
            ax.yaxis.set_major_locator(MaxNLocator(5))
            
            # Add grid
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Optimize plot boundaries
            y_margin = (max(partial_predictions) - min(partial_predictions)) * 0.1
            ax.set_ylim(min(partial_predictions) - y_margin, max(partial_predictions) + y_margin)
            
            return canvas
            
        except Exception as e:
            print(f"Error creating partial dependence plot: {e}")
            traceback.print_exc()
            
            # Create empty plot with error message
            fig = Figure(figsize=(10, 6))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, f"Error creating plot: {str(e)}", 
                    ha='center', va='center', transform=ax.transAxes, color='red')
            return canvas