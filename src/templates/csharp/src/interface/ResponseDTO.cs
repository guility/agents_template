namespace DddTemplate.Interface;

using System.Text.Json;
using Microsoft.AspNetCore.Mvc;

/// <summary>
/// Standard API response DTO following REST conventions
/// </summary>
public class ResponseDTO
{
    public bool Success { get; set; }
    public object? Data { get; set; }
    public string? Error { get; set; }

    public static ResponseDTO Ok(object? data = null) => new()
    {
        Success = true,
        Data = data
    };

    public static ResponseDTO Fail(string error) => new()
    {
        Success = false,
        Error = error
    };
}

/// <summary>
/// Base request DTO for API operations
/// </summary>
public abstract class RequestDTO
{
    public string? Id { get; set; }
    public Dictionary<string, object?>? Params { get; set; }
}

/// <summary>
/// Extension methods for ActionResult to standardize responses
/// </summary>
public static class ResponseExtensions
{
    public static IActionResult ToActionResult(this ResponseDTO response)
    {
        if (response.Success)
        {
            return response.Data switch
            {
                null => new NoContentResult(),
                _ => new OkObjectResult(response)
            };
        }
        
        return new BadRequestObjectResult(response);
    }
}
